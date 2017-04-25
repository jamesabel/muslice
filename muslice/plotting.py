
import matplotlib
# AGG png raster graphics – high quality images using the Anti-Grain Geometry engine
matplotlib.use('Agg')
import matplotlib.pyplot as plt


def plot_rms_peak(rms, peak, file_path):
    line_width = 1.0
    plt.plot(rms, label='rms', linewidth=line_width)
    plt.plot(peak, label='peak', linewidth=line_width)
    plt.savefig(file_path, dpi=600)
    plt.close()


def plot_meters(meters, file_path):
    fig, ax = plt.subplots()
    for meter in meters:
        ax.plot(meters[meter], label=meter, linewidth=1.0)
    ax.legend(loc='lower center', ncol=len(meters))
    plt.savefig(file_path, dpi=600)
    plt.close()
