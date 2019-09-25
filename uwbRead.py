# coding: utf-8

import socket
try:
    import _thread
except:
    import thread as _thread
from struct import *

class DataCollector():
    def __init__(self):
        try:
            from tkinter import Tk, Label, Entry, Button, messagebox
        except:
            from Tkinter import Tk, Label, Entry, Button
            import tkMessageBox as messagebox

        def set_exp_window():
            for i in range(self.tag_n):
                Label(self.window, text='tag: %d' % i).grid(row=i, column=0)
                Button(self.window, text='start', command=lambda a=i: self.start_tag(a)).grid(row=i, column=1)
                Button(self.window, text='stop', command=lambda a=i: self.stop_tag(a)).grid(row=i, column=2)
                Button(self.window, text='inspect', command=lambda a=i: self.draw_route(a)).grid(row=i, column=3)

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
        self.tag_ok = dict()
        self.id_tag = dict()
        self.id_file = dict()

    def socket(self):
        print('Creating socket...')
        host="192.168.0.201"
        port=6666
        s=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
        s.connect((host,port))
        print('Socket connected.')

        while 1:
            data=s.recv(73)

            if data[4:8] != 'PRES':
                continue

            format = '=iibddddddq'
            # format: ['labelId', 'seqId', 'lock', 'x', 'y', 'z', 'vx', 'vy', 'vz', 'time']
            res = unpack(format, data[8:])

            if res[0] not in self.buffer:
                self.buffer[res[0]] = list()
                self.tag_ok[res[0]] = True
            self.buffer[res[0]].append(res)

        s.close()

    def start_tag(self, i):
        if i in self.id_tag:
            tag = self.id_tag[i]
            try:
                self.buffer[tag].clear()
            except:
                self.buffer[tag] = list()
            return

        for tag in self.tag_ok:
            if self.tag_ok[tag]:
                print(tag)
                try:
                    self.buffer[tag].clear()
                except:
                    self.buffer[tag] = list()
                self.tag_ok[tag] = False
                self.id_tag[i] = tag
                for a in self.id_tag:
                    print(a, self.id_tag[a])
                return
        print('Error: no available tag.')

    def check_id(self, i):
        if i not in self.id_tag:
            print('Error: tag not started1.')
            return False
        tag = self.id_tag[i]
        if self.tag_ok[tag] == True:
            print('Error: tag not started2.')
            return False
        return True

    def stop_tag(self, i):
        if not self.check_id(i):
            return

        if i not in self.id_file:
            self.id_file[i] = 0
        self.id_file[i] += 1

        with open('%d_%04d.txt' % (i, self.id_file[i]), 'w') as f:
            for line in self.buffer[tag]:
                f.write(str(line))
                f.write('\n')

        Label(self.window, text='id: %d' % self.id_file[i]).grid(row=i, column=4)

        self.buffer.pop(tag)
        self.tag_ok[tag] = True
        self.id_tag.pop(i)

    def draw_route(self, i):
        if not self.check_id(i):
            return

        from utils import TrackPlot
        tp = TrackPlot(self.buffer(self.id_tag[i]))
        tp.draw_route()

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
