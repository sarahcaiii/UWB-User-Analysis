# coding: utf-8

import os
import socket
import _thread
from struct import *

class Tag():
    def __init__(self, tag_id, file_id):
        self.id = tag_id

        self.working = False

        self.label = None
        self.buttons = dict()
        self.status = None

        self.buffer = list()
        self.save_id = None
        self.file_id = file_id

    def initial_buttons(self, window):
        from tkinter import Button, Label
        self.label = Label(window, text='tag: %d' % self.id)
        self.buttons['start'] = Button(window, text='start', command=self.start_tag)
        self.buttons['stop'] = Button(window, text='stop', command=self.stop_tag)
        self.buttons['inspect'] = Button(window, text='inspect', command=self.draw_route)
        self.buttons['light'] = Button(window, bg='Red')
        self.status = Label(window, text='sleeping')

        def set_ok_color(tag_id, bu):
            import time
            while 1:
                bu['bg'] = 'Green' if self.working else 'Red'
                self.working = False
                time.sleep(2)

        _thread.start_new_thread(set_ok_color, (self.id, self.buttons['light']))

    def show_buttons(self):
        self.label.grid(row=self.id, column=0)
        self.buttons['start'].grid(row=self.id, column=1)
        self.buttons['stop'].grid(row=self.id, column=2)
        self.buttons['inspect'].grid(row=self.id, column=3)
        self.buttons['light'].grid(row=self.id, column=4)
        self.status.grid(row=self.id, column=5)

    def start_tag(self):
        if not self.working:
            print('Error: no available tag.')
            return

        self.buffer.clear()
        self.status['text'] = 'working'
        if self.save_id:
            self.save_id.grid_forget()

    def stop_tag(self):
        if self.status['text'] != 'working':
            return

        self.file_id[0] += 1
        with open('./results/%04d.txt' % self.file_id[0], 'w') as f:
            for line in self.buffer:
                f.write(str(line))
                f.write('\n')

        with open('config.txt', 'w') as f:
            f.write(str(self.file_id[0]))
            f.write('\n')

        self.status['text'] = 'stopped\t id: %04d' % self.file_id[0]

    def draw_route(self):
        if not self.buffer:
            print('no data for plotting.')
            return

        from utils import TrackPlot

        try:
            tp = TrackPlot(self.buffer)
            tp.draw_route()
        except:
            print('not enough data for plotting.')

    def append_buffer(self, data):
        if self.status['text'] == 'working':
            self.buffer.append(data)

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

            self.tag[tag_id] = Tag(tag_id, self.file_id)
            self.tag[tag_id].initial_buttons(self.window)
            self.tag[tag_id].show_buttons()

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
        self.tag = dict()

        try:
            with open('config.txt', 'r') as f:
                self.file_id = [int(f.readline().strip())]
        except:
            self.file_id = [0]

    def socket(self):
        print('Creating socket...')
        s = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
        s.connect(('127.0.0.1', 6666))
        print('Socket connected.')

        while 1:
            data=s.recv(73)

            if data[4:8] != b'PRES':
                continue

            # format: ['labelId', 'seqId', 'lock', 'x', 'y', 'z', 'vx', 'vy', 'vz', 'time']
            res = unpack('=iibddddddq', data[8:])

            if res[0] in self.tag:
                self.tag[res[0]].append_buffer(res)
                self.tag[res[0]].working = True

        s.close()

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
