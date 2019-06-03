# -*- coding: UTF-8 -*-
# Copyright (C) 2019, Raffaello Bonghi <raffaello@rnext.it>
# All rights reserved
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions
# are met:
#
# 1. Redistributions of source code must retain the above copyright
#    notice, this list of conditions and the following disclaimer.
# 2. Redistributions in binary form must reproduce the above copyright
#    notice, this list of conditions and the following disclaimer in the
#    documentation and/or other materials provided with the distribution.
# 3. Neither the name of the copyright holder nor the names of its
#    contributors may be used to endorse or promote products derived
#    from this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND
# CONTRIBUTORS "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING,
# BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS
# FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT
# HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
# SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO,
# PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS;
# OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY,
# WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE
# OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE,
# EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.


from datetime import timedelta
# control command line
import curses
# Graphics elements
from .jtopguilib import (check_curses,
                         linear_percent_gauge,
                         make_gauge_from_percent,
                         plot_name_info)


def strfdelta(tdelta, fmt):
    """ Print delta time
        - https://stackoverflow.com/questions/8906926/formatting-python-timedelta-objects
    """
    d = {"days": tdelta.days}
    d["hours"], rem = divmod(tdelta.seconds, 3600)
    d["minutes"], d["seconds"] = divmod(rem, 60)
    return fmt.format(**d)


def plot_CPUs(stdscr, offest, list_cpus, width):
    max_bar = int(float(width) / 2.0)
    for idx, cpu in enumerate(list_cpus):
        # Split in double list
        start = max_bar + 1 if idx >= len(list_cpus) / 2 and len(list_cpus) > 4 else 0
        off_idx = idx - len(list_cpus) / 2 if idx >= len(list_cpus) / 2 and len(list_cpus) > 4 else idx
        # Plot the linear gauge
        gauge = make_gauge_from_percent(cpu)
        if 'value' in gauge:
            gauge["percent"] = cpu['governor'] + " - " + str(gauge['value']) + "%"
        linear_percent_gauge(stdscr, gauge, max_bar, offest + off_idx, start)
    if len(list_cpus) > 4:
        return offest + idx / 2 + 1
    else:
        return offest + idx + 1


@check_curses
def plot_temperatures(stdscr, offset, data, start=0):
    # Plot title
    stdscr.addstr(offset, start, " {0:<10} {1}".format("[Sensor]", "[Temp]"), curses.A_BOLD)
    counter = 1
    for key, value in data.items():
        stdscr.addstr(offset + counter, start,
                      "{0:<10} {1:>4.2f}{2}".format(key, value['value'][-1],
                                                    value['unit']))
        counter += 1


@check_curses
def plot_voltages(stdscr, offset, data, start=0):
    # Plot title
    stdscr.addstr(offset, start, " {0:<10} {1}".format("[Power]", " [Cur/Avr]"), curses.A_BOLD)
    counter = 1
    for key, value in data.items():
        stdscr.addstr(offset + counter, start,
                      "{0:<10} {1:^4}mW/{2:^4}mW".format(key, int(value['current'][-1]),
                                                         int(value['average'][-1]))
                      )
        counter += 1


@check_curses
def plot_other_info(stdscr, offset, jetson, width, start=0):
    # Title menu
    stdscr.addstr(offset, start, "{:^20}".format("[Info]"), curses.A_BOLD)
    counter = 1
    # Model board information
    uptime_string = strfdelta(timedelta(seconds=jetson.uptime), "{days} days {hours}:{minutes}:{seconds}")
    plot_name_info(stdscr, offset + counter, start, "UpT", uptime_string)
    counter += 1
    # FAN status
    if jetson.fans:
        for fan in jetson.fans:
            FAN_VALUE = {'name': 'FAN',
                         'value': int(fan[-1]),
                         }
            linear_percent_gauge(stdscr, FAN_VALUE, width,
                                 offset=offset + counter, start=start)
            counter += 1
    # Plot MTS
    if 'MTS' in jetson.stats:
        stdscr.addstr(offset + counter, start, "MTS:", curses.A_BOLD)
        MTS_FG = {'name': ' FG',
                  'value': int(jetson.stats['MTS']['fg']),
                  }
        linear_percent_gauge(stdscr, MTS_FG, width,
                             offset=offset + counter + 1, start=start)
        MTS_BG = {'name': ' BG',
                  'value': int(jetson.stats['MTS']['bg']),
                  }
        linear_percent_gauge(stdscr, MTS_BG, width,
                             offset=offset + counter + 2, start=start)
        counter += 3
    # APE frequency
    if 'APE' in jetson.stats:
        plot_name_info(stdscr, offset + counter, start, "APE", str(jetson.stats['APE']) + "MHz")
        counter += 1
    # NVP Model
    if jetson.nvpmodel:
        str_nvp = jetson.nvpmodel['name'] + " - " + str(jetson.nvpmodel['mode'])
        plot_name_info(stdscr, offset + counter, start, "NV Power", str_nvp)
        counter += 1
    # IP address and Hostname
    if jetson.local_interfaces:
        plot_name_info(stdscr, offset + counter, start, "Hostname", jetson.local_interfaces["hostname"])
        counter += 1
        for name, ip in jetson.local_interfaces["interfaces"].items():
            plot_name_info(stdscr, offset + counter, start, " " + name, ip)
            counter += 1
# EOF
