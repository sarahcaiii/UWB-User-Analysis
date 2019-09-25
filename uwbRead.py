import socket
import _thread
from struct import *

class DataCollector():
    def __init__(self):
        from tkinter import Tk, Label, Entry, Button, messagebox

        def set_exp_window():
            for i in range(self.tag_n):
                Label(self.window, text='tag: %d' % i).grid(row=i, column=0)
                Button(self.window, text='start', command=lambda: self.start_tag(i)).grid(row=i, column=1)
                Button(self.window, text='stop', command=lambda: self.stop_tag(i)).grid(row=i, column=2)

        def get_initial_window():
            initial_window = Tk()
            initial_window.title('uwb 数据采集')
            initial_window.geometry('300x300')

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
            Button(initial_window, command=lambda: set_tag_n(initial_window, e)).grid()

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

            if not self.buffer[res[0]]:
                self.buffer[res[0]] = list()
                self.tag_ok[res[0]] = True
            self.buffer[res[0]].append(res)

        s.close()

    def start_tag(self, i):
        for tag in self.tag_ok:
            if self.tag_ok[tag] == True:
                self.buffer[tag].clear()
                self.tag_ok[tag] = False
                self.id_tag[i] = tag
                return
        print('Error: no available tag.')

    def stop_tag(self, i):
        if i not in self.id_tag or self.tag_ok[tag] == True:
            print('Error: tag not started.')
            return

        if not self.id_file[i]:
            self.id_file[i] = 0
        self.id_file[i] += 1

        with open('%d_%4d.txt' % (i, self.id_file[i]), 'w') as f:
            for line in self.buffer[tag]:
                f.write(line)
                f.write('\n')

        self.buffer[tag].clear()
        self.tag_ok[tag] = True
        self.id_tag.pop(i)

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
