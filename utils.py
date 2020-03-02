import matplotlib.pyplot as plt
import matplotlib.path as mpath
import numpy as np

def get_data_from_string(data_string):
    '''
    input: uwb data string that saved in files
    output: data list ['labelId', 'seqId', 'lock', 'x', 'y', 'z', 'vx', 'vy', 'vz', 'time(todo)']
    '''
    return [float(x) for x in data_string.strip(' ()\n').split(',')]

def get_data_from_file(file_name):
    buffer = list()
    with open(file_name) as f:
        for line in f.readlines():
            buffer.append(get_data_from_string(line))
    return buffer

class PlotFile:
    def __init__(self, file_name):
        super(PlotFile, self).__init__()
        self.data_list = list()

        with open(file_name, 'r') as f:
            for line in f.readlines():
                self.data_list.append(get_data_from_string(line))

        self.data_list = np.around(np.asarray(self.data_list), decimals = 3)

    def smooth(self, c):
        N = 50
        weights=np.hanning(N)
        return np.convolve(weights/weights.sum(),c)[N-1:-N+1]

    def draw_x(self, pos):
        plt.subplot(pos)
        plt.plot(self.data_list[:, 3])
        plt.plot(self.smooth(self.data_list[:, 3]))

    def draw_y(self, pos):
        plt.subplot(pos)
        plt.plot(self.smooth(self.data_list[:, 4]))

    def draw_route(self, pos):
        plt.subplot(pos)
        plt.scatter(self.data_list[:, 3], self.data_list[:, 4], s=2)
        plt.scatter(self.smooth(self.data_list[:, 3]), self.smooth(self.data_list[:, 4]), s=2)

def draw_test(plot):
    plot.draw_x(311)
   #plot.draw_y(312)
    plot.draw_route(313)
    plt.show()

def heat_test(plot):
    from scipy.stats import gaussian_kde
    x = plot.smooth(plot.data_list[:, 3])
    y = plot.smooth(plot.data_list[:, 4])
    xy = np.vstack([x,y])
    z = gaussian_kde(xy)(xy)

    fig, ax = plt.subplots()
    ax.scatter(x, y, c=z, s=5, edgecolor='')
    plt.show()

class TrackPlot:
    def __init__(self, data_list):
        super(TrackPlot, self).__init__()
        self.data_list = list()
        for data in data_list:
            self.data_list.append([d for d in data])

        self.data_list = np.asarray(self.data_list)

    def smooth(self, c):
        N = 50
        weights=np.hanning(N)
        return np.convolve(weights/weights.sum(),c)[N-1:-N+1]

    def draw_route(self):
        from scipy.stats import gaussian_kde
        x = self.smooth(self.data_list[:, 3])
        y = self.smooth(self.data_list[:, 4])
        xy = np.vstack([x,y])
        z = gaussian_kde(xy)(xy)

        fig, ax = plt.subplots()
        plt.xlim((-20, 25))
        plt.ylim((-10, 10))

        bg = plt.imread('tmall.png')
        ax.imshow(bg, extent=[-33, 38, -37, 40])
        ax.scatter(x, y, c=z, s=3)

        plt.show()

def main():
    file_name = './results/0001.txt'

    buffer = get_data_from_file(filr_name)
    plot = TrackPlot(buffer)
    plot.draw_route()
    #heat_test(plot)
    #animation_test(plot)


if __name__ == '__main__':
    main()
