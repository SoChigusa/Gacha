from flask import Flask, render_template
from io import BytesIO
import base64
import matplotlib.pyplot as plt
import math
import numpy as np

app = Flask(__name__)


def fig_to_base64_img(fig):
  io = BytesIO()
  fig.savefig(io, format='png')
  io.seek(0)
  base64_img = base64.b64encode(io.read()).decode()

  return base64_img


@app.route('/')
def home():
  q = 0.01

  def plot(mode):
    # probability calculation
    def pn(n, k):
      return math.comb(n, k) * np.power(q, k) * np.power(1 - q, n - k)

    def Pn(n, goal):
      pn_list = np.array([pn(int(n), k) for k in range(goal)])
      if(mode == 0):
        return 100 * (1 - np.sum(pn_list))
      if(mode == 1):
        return 100 * np.sum(pn_list)
      if(mode == 2):
        pn_list2 = np.array([pn(int(n + 10), k) for k in range(goal)])
        return 100 * (np.sum(pn_list) - np.sum(pn_list2))

    # plot settings
    plt.rcParams['font.family'] = 'Hiragino Maru Gothic Pro'
    fig = plt.figure()
    ax = fig.add_subplot(1, 1, 1)
    ax.set_xlim(0, 1000)
    ax.set_xlabel('ガチャを引く回数', size=20)
    ax.tick_params(labelsize=15)

    # secondary axis settings
    def num2yen(n):
      return 0.03 * n

    def yen2num(y):
      return y // 0.03

    axR = ax.secondary_yaxis('right')
    axR.tick_params(labelright=False)
    axT = ax.secondary_xaxis('top', functions=(num2yen, yen2num))
    axT.set_xlabel('金額【万円】', size=20)
    axT.set_xticks([0, 6, 12, 18, 24, 30])
    axT.tick_params(labelsize=15)

    # settings for specific plots
    if(mode == 0):
      ax.set_ylabel('完凸済み確率【％】', size=20)
      ax.set_ylim(0, 100)
    if(mode == 1):
      ax.set_ylabel('未完凸確率【％】', size=20)
      ax.set_yscale('log')
      ax.set_ylim(1e-3, 100)
    if(mode == 2):
      ax.set_ylabel('完凸に必要な回数の分布', size=20)
      ax.set_yticks([])
      ax.set_ylim(0, 2.5)
      axR.set_yticks([])

    # plot accumulated probability
    for num_ten in range(5):
      x = np.linspace(200 * num_ten, 200 * (num_ten + 1), 21)
      y = [Pn(n, 5 - num_ten) for n in x]
      ax.plot(x, y, c='b', lw=1)
      x = [200 * (num_ten + 1), 200 * (num_ten + 1)]
      y = [Pn(x[0], 5 - num_ten), Pn(x[1], 4 - num_ten)]
      ax.plot(x, y, c='b', lw=1)

    # auxiliary lines
    for num_ten in range(1, 5):
      x = [200 * num_ten, 200 * num_ten]
      y = [0, 100]
      ax.plot(x, y, c='black', lw=1, ls=':')

    # adjust and output
    plt.tight_layout()
    return fig_to_base64_img(fig)

  img = [plot(i) for i in range(3)]
  return render_template('index.html', img0=img[0], img1=img[1], img2=img[2])
