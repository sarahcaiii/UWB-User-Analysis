import numpy as np
from scipy import signal
from utils import get_data_from_file

class Preprocess:
    def __init__(self, data_list):
        self.data_list = data_list
        #print(self.data_list)

    def extreme_filter(self):
        data_list = list()
        for data in self.data_list:
            if data[3] > -3 and data[3] < 12 \
            and data[4] > -5 and data[4] < 15\
            and data[5] < 3 and data[5] > 0 \
            and data[6] < 2 and data[7] < 2:
                data_list.append(data)
        self.data_list = data_list

    def outlier_filter(self):
        data_list = list()

        def smooth(c, N=7):
            weights = np.hanning(N)
            tmp = np.convolve(weights / weights.sum(), c)[N - 1:-N + 1]

            residual = np.asarray(tmp) - np.asarray(c[3:-3])
            mean = np.mean(residual)
            std = np.std(residual)

            return tmp, mean, std

        x_tmp, x_mean, x_std = smooth(np.asarray(self.data_list)[:, 3])
        y_tmp, y_mean, y_std = smooth(np.asarray(self.data_list)[:, 4])

        for i, data in enumerate(self.data_list[3:-3]):
            if np.abs(data[3] - x_tmp[i]) < 3.0 * x_std \
            and np.abs(data[4] - y_tmp[i]) < 3.0 * y_std:
                data_list.append(data)

def main():
    file_name = './results/0001.txt'
    data = Preprocess(get_data_from_file(file_name))
    data.extreme_filter()
    data.outlier_filter()

if __name__ == '__main__':
    main()
