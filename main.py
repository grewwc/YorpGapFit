import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
from sklearn import svm
from typing import List, Tuple
from functools import lru_cache


@lru_cache
def read_data(filename: str = None):
    merge_df = pd.read_csv(filename)
    x, y = merge_df['diameter (km)'], merge_df['Period (h)']
    x, y = np.log10(x), -np.log10(y)
    X = np.array(list(zip(x, y)))
    return X


def line(X, k, b, gap=0.5):
    return k * X[:, 0] + b + gap


def classify(X, k, b, gap) -> List[int]:
    upper_index = X[:, 1] > line(X, k=k, b=b, gap=gap)  # label 1
    lower_index = X[:, 1] < line(X, k=k, b=b, gap=-gap)   # label 2
    #  [0,1,1,1,0]
    labels = [-1] * len(X)
    for i in range(len(X)):
        if upper_index[i]:
            labels[i] = 1
        elif lower_index[i]:
            labels[i] = 0
    labels = np.array(labels)
    return labels


def split(X, labels):
    ratio = 1
    with_labels = labels != -1
    lower = labels == 0
    upper = labels == 1
    lower_count = sum(lower)
    upper_count = sum(upper)

    X_upper_train, y_upper_train = X[upper], labels[upper]
    X_lower_train, y_lower_train = X[lower], labels[lower]

    random_index = np.arange(int(upper_count))
    np.random.shuffle(random_index)
    X_upper_train, y_upper_train = X_upper_train[random_index], y_upper_train[random_index]
    upper_count = int(ratio * upper_count)
    X_upper_train, y_upper_train = X_upper_train[:upper_count, :], y_upper_train[:upper_count]
    random_index = np.arange(lower_count)
    np.random.shuffle(random_index)
    X_lower_train, y_lower_train = X_lower_train[random_index], y_lower_train[random_index]

    X_test, y_test = X[~with_labels], labels[~with_labels]
    X_train = np.r_[X_upper_train, X_lower_train]
    y_train = np.r_[y_upper_train, y_lower_train]
    # print(f'upper ~ lower: {upper_count}~{lower_count}')
    return (X_train, y_train), (X_test, y_test)


def fit(X, labels) -> Tuple[float, float]:
    clf = svm.LinearSVC(dual='auto')
    fit = clf.fit(X, labels)
    coefs = fit.coef_[0]
    intercept = fit.intercept_[0]
    k = -coefs[0]/coefs[1]
    b = -intercept/coefs[1]
    return k, b, clf


def fill_gap(k, b, gap, color, savefig_name=None):
    x = np.linspace(0, 2.5, 100)
    y = k*x + b
    lower = y-gap/2
    upper = y+gap/2
    plt.plot(x, y-gap/2, color=color)
    plt.plot(x, y+gap/2, color=color)
    plt.fill_between(x, lower, upper, color='grey', alpha=0.5)
    if savefig_name:
        plt.savefig(savefig_name)


def plot_original_data():
    filename = "~/asteroid_dataframe.csv"   # the original data file name (csv format)
    X = read_data(filename)
    plt.xlim([0, 3])
    plt.scatter(X[:, 0], X[:, 1], s=1.0)
    plt.xlabel('Diameter (km)')
    plt.ylabel('Period (h)')
    # plot the gap
    fill_gap(-0.6, -1.2, gap=0.4, color='k')

    plt.show()


def fit_params(init_k, savefig_filename=None):
    # 读取数据
    filename = "~/asteroid_dataframe.csv"   # the original data file name (csv format)
    X = read_data(filename)
    k, b, gap = init_k, -1.2, 0.2
    clf = None
    for i in range(1000):
        labels = classify(X, k=k, b=b, gap=gap)
        (X_train, y_train), (X_test, y_test) = split(X, labels)

        # 获取直线斜率
        k, b, clf = fit(X_train, y_train)
        print(f'Iteration: {i}, k: {k}, b: {b}')

    y_pred = clf.predict(X)
    X1 = X[y_pred == 1]
    X2 = X[y_pred == 0]
    plt.scatter(X1[:, 0], X1[:, 1], s=1.0)
    plt.scatter(X2[:, 0], X2[:, 1], s=1.0)
    

    x_min, x_max = 0, 3
    x = np.linspace(x_min, x_max, 100)
    plt.plot(x, k * x + b)
    plt.plot(x, k * x + b+gap)
    plt.plot(x, k * x + b-gap)
    plt.fill_between(x, k * x + b-gap, k * x + b+gap, color='grey', alpha=0.5)
    plt.legend()
    plt.xlabel('Diameter (km)')
    plt.ylabel('Period (h)')
    if savefig_filename:
        plt.savefig(savefig_filename)
    plt.show()

if __name__ == '__main__':
    fit_params(init_k=-0.6)
