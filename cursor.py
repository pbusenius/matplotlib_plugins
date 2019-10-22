from matplotlib.widgets import _SelectorWidget


class HarmonicCursor(_SelectorWidget):
    def __init__(self, ax, num_of_cursor=10, color="black", onselect=None, animate_text=False):
        _SelectorWidget.__init__(self, ax, onselect, useblit=True)
        self.ax = None
        self.num_of_cursors = num_of_cursor
        self.color = color
        self.animate_text = animate_text
        self.start = None
        self.stop = None
        self.steps = 0
        self.text = 0

        # Reset canvas so that `new_axes` connects events.
        self.canvas = None
        self._init_axes(ax)

    def set_num_of_cursors(self, num_of_cursors):
        if num_of_cursors <= 1:
            raise ValueError("Value must be >= 2")
        self.num_of_cursors = num_of_cursors
        self.update_cursor()
        self.update()

    def _init_cursor(self):
        if self.animate_text:
            self.artists.append(self.ax.text(0, 0, "", bbox={"facecolor": "w", "alpha": 0.5, "pad": 5}, fontsize=10))

        for i in range(self.num_of_cursors):
            tmp_line = self.ax.axvline(x=0)
            self.artists.append(tmp_line)

    def update_cursor(self):
        if len(self.artists) == 0:
            self._init_cursor()

        self.steps = (self.stop - self.start) / (self.num_of_cursors - 1)

        x = self.ax.get_xlim()[1] * 0.01
        y = self.ax.get_ylim()[1] * 0.9

        if self.animate_text:
            self.artists[0].set_position((x, y))
            self.artists[0].set_text("Cursors: {} Delta: {:.2f}".format(len(self.artists)-1, self.steps))

            for i in range(self.num_of_cursors):
                self.artists[i + 1].set_xdata(self.start + i * self.steps)
                self.artists[i + 1].set_visible(True)
        else:
            for i in range(self.num_of_cursors):
                self.artists[i].set_xdata(self.start + i * self.steps)
                self.artists[i].set_visible(True)

        self.update()

    def clear(self):
        for i in self.artists:
            i.remove()

        self.artists = []

    def _init_axes(self, ax):
        self.ax = ax
        if self.canvas is not ax.figure.canvas:
            if self.canvas is not None:
                self.disconnect_events()

            self.canvas = ax.figure.canvas
            self.connect_default_events()

    def _press(self, event):
        """on button press event"""
        self.start, y = self._get_data(event)
        return False

    def _release(self, event):
        """on button release event"""
        if self.onselect is not None:
            self.onselect((self.start, self.stop, self.steps,
                          [self.start + i * self.steps for i in range(self.num_of_cursors)]))
        return False

    def _onmove(self, event):
        """on motion notify event"""
        self.stop, _ = self._get_data(event)
        self.update_cursor()
        return False


def on_select(event):
    print(event[0], event[1], event[2], event[3])


if __name__ == "__main__":
    import matplotlib.pyplot as plt
    import scipy.io.wavfile as wav
    import numpy as np

    rate, data = wav.read("test.wav")
    f, (ax1, ax2) = plt.subplots(2, 1)

    fft_data = np.abs(np.fft.fft(data))

    ax1.specgram(data, NFFT=1024, Fs=rate, mode="magnitude")
    ax2.plot(np.fft.fftfreq(fft_data.size, d=1/rate), fft_data)
    ax2.set_xlim(0, int(rate/2))

    harmonic_cursor = HarmonicCursor(ax=ax2, onselect=on_select, num_of_cursor=20, color="red", animate_text=True)

    plt.show()

