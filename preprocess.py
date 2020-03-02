from utils import get_data_from_file

class Preprocess:
    def __init__(self, data_list):
        self.data_list = data_list
    def extreme_filter(self):
        data_list = list()
    def outlier_filter(self):
        data_list = list()


def main():
    file_name = './results/0001.txt'
    data = Preprocess(get_data_from_file(file_name))
    data.extreme_filter()
    data.outlier_filter()

if __name__ == '__main__':
    main()
