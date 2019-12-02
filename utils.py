import matplotlib.pyplot as plt
import matplotlib.path as mpath
import numpy as np
import math

def get_data_from_string(data_string):
    '''
    input: uwb data string that saved in files
    output: data list ['labelId', 'seqId', 'lock', 'x', 'y', 'z', 'vx', 'vy', 'vz', 'time(todo)']
    '''
    return [float(x) for x in data_string.strip(' ()\n').split(',')]

def get_data_list_from_file(file_name):
    data_list = list()
    with open(file_name, 'r') as f:
        for line in f.readlines():
            if line != '\n':
                data_list.append(get_data_from_string(line))
    return data_list

class TrackPlot:
    def __init__(self, data_list):
        super(TrackPlot, self).__init__()
        self.data_list = list()
        for data in data_list:
            self.data_list.append([d for d in data])

        self.data_list = np.asarray(self.data_list)

    def extreme_filter(self, speed=False):
        index = list()
        for (i, data) in enumerate(self.data_list):
            if data[5] >= 0 and data[5] < 2.5 \
            and data[3] > -10 and data[3] < 25 \
            and data[4] > -10 and data[4] < 12:
                if not speed or (abs(data[6]) < 4 and abs(data[7]) < 4):
                    index.append(i)

        self.data_list = self.data_list[index]

    def outlier_filter(self, range_list, sigma=2):
        for k in range_list:
            data_list = self.data_list[:,k]

            smooth_n = 17
            smooth_list = self.smooth(data_list, smooth_n)[smooth_n//2:-smooth_n//2-1]
            #smooth_list = self.smooth(data_list, smooth_n)[smooth_n:-smooth_n]
            res_list = smooth_list - data_list[smooth_n:-smooth_n]
            res_mean = np.mean(res_list)
            res_std = np.std(res_list, ddof=1)

            index = list()
            for i in range(len(res_list)):
                if res_list[i] < res_mean - sigma * res_std or res_list[i] > res_mean + sigma * res_std:
                    continue
                index.append(i)

            self.data_list = np.append(np.append(self.data_list[:smooth_n], self.data_list[index], axis=0), self.data_list[-smooth_n:-1], axis=0)

    def segmentation(self):
        degree_threshold = 5
        hold_index_list = []
        previous_azimuth = 1000

        for data_id, data in enumerate(self.data_list[:-1]):
            next_data = self.data_list[data_id + 1]
            diff_vector = next_data[3:5] - data[3:5]
            azimuth = (math.degrees(math.atan2(*diff_vector)) + 360) % 360

            if abs(azimuth - previous_azimuth) > degree_threshold:
                hold_index_list.append(data_id)
                previous_azimuth = azimuth
        hold_index_list.append(len(self.data_list) - 1)
        self.data_list = self.data_list[hold_index_list]

    def preprocess(self, test=False):
        #plt.scatter(self.data_list[:,3], self.data_list[:,4], s=2, label='1')
        self.extreme_filter()
        if test:
            plt.scatter(self.data_list[:,3], self.data_list[:,4], s=2, label='2')
        self.extreme_filter(True)
        if test:
            plt.scatter(self.data_list[:,3], self.data_list[:,4], s=2, label='3')
        self.outlier_filter(range(3, 9))
        if test:
            plt.scatter(self.data_list[:,3], self.data_list[:,4], s=2, label='4')
            plt.legend()

    def interp(self, c, N=51):
        from scipy.signal import savgol_filter
        return savgol_filter(c, N, 2, mode='nearest')

    def smooth(self, c, N=17):
        weights=np.hanning(N)
        return np.convolve(weights/weights.sum(),c)[N-1:-N+1]

    def draw_route(self):
        from scipy.stats import gaussian_kde
        #x = self.interp(self.data_list[:, 3])
        #y = self.interp(self.data_list[:, 4])
        x = self.data_list[:, 3]
        y = self.data_list[:, 4]
        xy = np.vstack([x,y])
        z = gaussian_kde(xy)(xy)

        fig, ax = plt.subplots()
        plt.xlim((-20, 25))
        plt.ylim((-10, 10))

        bg = plt.imread('tmall.png')
        ax.imshow(bg, extent=[-31, 38, -37, 43])
        #ax.scatter(x, y, c=z, s=3)
        ax.plot(x, y)

def draw_test():
    file_name = './results/0121.txt'
    data_list = get_data_list_from_file(file_name)
    plot = TrackPlot(data_list)
    plot.preprocess()
    plot.draw_route()
    plt.show()

def save_test():
    for i in range(342, 401):
        file_name = './results/%04d.txt' % i
        data_list = get_data_list_from_file(file_name)
        plot = TrackPlot(data_list)
        #plot.preprocess()
        plot.draw_route()
        plt.savefig('./raw_figs/%04d.png' % i)
        plt.close()
        print('%04d.png' % i)


if __name__ == '__main__':
    draw_test()
    #save_test()
