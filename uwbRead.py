# coding: utf-8

import os
import socket
import _thread
from struct import *

class DataCollector():
    def __init__(self):
        from tkinter import Tk, Label, Entry, Button, messagebox

        def set_exp_window():
            for i in range(100, 100 + self.tag_n):
                ls = list()
                l = Label(self.window, text='tag: '); l.grid(row=i, column=0)
                e = Entry(self.window);e.grid(row=i, column=1)
                bu = Button(self.window, text='ok');bu.grid(row=i, column=2)
                ls = [l, e, bu]
                command = (lambda event, b=e, c=ls: set_tag(b, c))
                bu.bind("<Button-1>", command)

        def set_tag(e, c):
            for s in c:
                s.grid_forget()
            tag_id = int(e.get())
            Label(self.window, text='tag: %d' % tag_id).grid(row=tag_id, column=0)
            self.tag_status[tag_id] = Label(self.window, text='sleeping');self.tag_status[tag_id].grid(row=tag_id, column=5)

            Button(self.window, text='start', command=lambda a=tag_id: self.start_tag(a)).grid(row=tag_id, column=1)
            Button(self.window, text='stop', command=lambda a=tag_id: self.stop_tag(a)).grid(row=tag_id, column=2)
            Button(self.window, text='inspect', command=lambda a=tag_id: self.draw_route(a)).grid(row=tag_id, column=3)

            bu = Button(self.window, bg='Red');bu.grid(row=tag_id, column=4)
            _thread.start_new_thread(set_ok_color, (tag_id, bu))

        def set_ok_color(tag_id, bu):
            import time

            while 1:
                if tag_id in self.tag_working and self.tag_working[tag_id]:
                    bu['bg'] = 'Green'
                else:
                    bu['bg'] = 'Red'

                self.tag_working[tag_id] = False
                time.sleep(2)

        def get_initial_window():
            initial_window = Tk()
            initial_window.title('uwb 数据采集')
            initial_window.geometry('400x400')

            def set_tag_n(window, e):
                if e.get().isdigit():
                    self.tag_n = int(e.get())
                    for s in window.grid_slaves():
                        s.grid_forget()
                    set_exp_window()
                else:
                    messagebox.showinfo(title='error', message='Input is invalid.')

            Label(initial_window, text='标签数量').grid()
            e = Entry(initial_window);e.grid()
            Button(initial_window, text='ok', command=lambda: set_tag_n(initial_window, e)).grid()

            return initial_window

        self.window = get_initial_window()
        self.buffer = dict()
        self.tag_working = dict()
        self.tag_status = dict()
        self.tag_save_id = dict()

        try:
            with open('config.txt', 'r') as f:
                self.file_id = int(f.readline().strip())
        except:
            self.file_id = 0

    def socket(self):
        print('Creating socket...')
        host="127.0.0.1"
        port=6666
        s=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
        s.connect((host,port))
        print('Socket connected.')

        while 1:
            data=s.recv(73)

            if data[4:8] != b'PRES':
                continue

            format = '=iibddddddq'
            # format: ['labelId', 'seqId', 'lock', 'x', 'y', 'z', 'vx', 'vy', 'vz', 'time']
            res = unpack(format, data[8:])

            if res[0] not in self.buffer:
                self.buffer[res[0]] = list()

            if res[0] in self.tag_status and self.tag_status[res[0]]['text'] == 'working':
                self.buffer[res[0]].append(res)

            self.tag_working[res[0]] = True

        s.close()

    def start_tag(self, tag):
        if not self.tag_working[tag]:
            print('Error: no available tag.')
            return

        self.buffer[tag].clear()
        self.tag_status[tag]['text'] = 'working'
        if tag in self.tag_save_id:
            self.tag_save_id[tag].grid_forget()

    def stop_tag(self, tag):
        if self.tag_status[tag]['text'] != 'working':
            return

        from tkinter import Label

        self.file_id += 1
        with open('./results/%04d.txt' % self.file_id, 'w') as f:
            for line in self.buffer[tag]:
                f.write(str(line))
                f.write('\n')

        with open('config.txt', 'w') as f:
            f.write(str(self.file_id))
            f.write('\n')

        self.tag_save_id[tag] = Label(self.window, text='id: %04d' % self.file_id);self.tag_save_id[tag].grid(row=tag, column=6)

        self.tag_status[tag]['text'] = 'stopped'

    def draw_route(self, tag):
        if not self.buffer[tag]:
            print('no data for plotting.')
            return

        from utils import TrackPlot
        tp = TrackPlot(self.buffer[tag])
        try:
            tp.draw_route()
        except:
            print('not enough data for plotting.')

    def run(self):
        try:
            _thread.start_new_thread(DataCollector.socket, (self, ))
        except:
            print('Error: unable to start thread')
        self.window.mainloop()

def main():
    dc = DataCollector()
    dc.run()

if __name__ == '__main__':
    main()
