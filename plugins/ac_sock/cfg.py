#!/usr/bin/env python
# -*- coding: utf-8 -*- 

from config import CMD

MIN_TRNASMIT_INTERVAL = 0.815

AC_SOCK_ALL = "Vše"



AC_SOCK_1 =     "Ložnice"

AC_SOCK_1_1 =   "Lampička"
AC_SOCK_1_2 =   "Pracovní stůl"
AC_SOCK_1_3 =   "Noční stůl"
AC_SOCK_1_4 =   "nic"

AC_SOCK_2 =     "Obývák a kuchyň"

AC_SOCK_2_1 =   "Lampa"
AC_SOCK_2_2 =   "Konferenční stůl"
AC_SOCK_2_3 =   "Osvětlení lednice"
AC_SOCK_2_4 =   "nic"

AC_SOCK_3 =     "Volné zásuvky"

AC_SOCK_3_1 =   "1"
AC_SOCK_3_2 =   "2"
AC_SOCK_3_3 =   "3"
AC_SOCK_3_4 =   "4"





AC_SOCK = {
    AC_SOCK_1: { AC_SOCK_1_1: {CMD.ON: "11111010001010001000111111011001", CMD.OFF: "11111010001010001000011111010101"},
                 AC_SOCK_1_2: {CMD.ON: "11111010001010001000101111011101", CMD.OFF: "11111010001010001000001111010011"},
                 AC_SOCK_1_3: {CMD.ON: "11111010001010001000110111011011", CMD.OFF: "11111010001010001000010111010111"},
               #  AC_SOCK_1_4: {CMD.ON: "11111010001010001000111011011000", CMD.OFF: "11111010001010001000011011010100"},
                 AC_SOCK_ALL: {CMD.ON: "11111010001010001000010011010110", CMD.OFF: "11111010001010001000100011011110"},
               },

    AC_SOCK_2: { AC_SOCK_2_1: {CMD.ON:"01101110110110110000111101111101", CMD.OFF: "01101110110110110000011101110011"},
                 AC_SOCK_2_2: {CMD.ON:"01101110110110110000101101111011", CMD.OFF: "01101110110110110000001101110111"},
                 AC_SOCK_2_3: {CMD.ON:"01101110110110110000110101111111", CMD.OFF: "01101110110110110000010101110000"},
               #  AC_SOCK_2_4: {CMD.ON:"01101110110110110000111001111100", CMD.OFF: "01101110110110110000011001110010"},
                 AC_SOCK_ALL: {CMD.ON:"01101110110110110000010001110001", CMD.OFF: "01101110110110110000100001111001"},
               },
           
    AC_SOCK_3: { AC_SOCK_3_1: {CMD.ON:"01011101101100110000111100010001", CMD.OFF: "01011101101100110000011100011001"},
                 AC_SOCK_3_2: {CMD.ON:"01011101101100110000101100010101", CMD.OFF: "01011101101100110000001100011101"},
                 AC_SOCK_3_3: {CMD.ON:"01011101101100110000110100010011", CMD.OFF: "01011101101100110000010100011011"},
                 AC_SOCK_3_4: {CMD.ON:"01011101101100110000111000010000", CMD.OFF: "01011101101100110000011000011000"},
                 AC_SOCK_ALL: {CMD.ON:"01011101101100110000010000011010", CMD.OFF: "01011101101100110000100000010110"},
               },
}

ITEMS              = AC_SOCK




