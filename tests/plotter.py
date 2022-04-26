import pandas as pd
from pathlib import Path
import matplotlib.pyplot as plt

BUFFER_SIZE = 10
TELEMETRY_STREAM = "telemetry.csv"
KELVIN_TO_CELSUIS_CONV = -273


def animate(frame):
    """
    Redraw MPL with latest telemetry data.
    :param frame: mpl ctx
    :type frame: [type]
    """
    # draw grid
    plt.cla()
    plt.xlabel('MCU Epoch (s)')
    plt.ylabel('Temperature Reading (°C)')
    plt.title('Temperature Driver Telemetry')
    plt.tight_layout()
    # check for file existance
    if not Path(__file__).parent.parent.joinpath(TELEMETRY_STREAM).exists():
        _log.warning("Telemetry stream: %s does not exist. Waiting ...", TELEMETRY_STREAM)
        return
    data = pd.read_csv(TELEMETRY_STREAM)
    # perform iteration mapping and queries
    t = np.fromiter(data['ts'], dtype=int)
    tc = np.fromiter(map(lambda x: kelvin_to_celsuis(x), data['tc']), dtype=int)
    tt = np.fromiter(map(lambda x: kelvin_to_celsuis(x), data['tt']), dtype=int)
    gp_low = np.fromiter(map(lambda x: kelvin_to_celsuis(
        x), data.loc[data['gp'] == 0]['tc']), dtype=int)
    gp_low_t = data.loc[data['gp'] == 0]['ts']
    gp_high = np.fromiter(map(lambda x: kelvin_to_celsuis(
        x), data.loc[data['gp'] == 1]['tc']), dtype=int)
    gp_high_t = data.loc[data['gp'] == 1]['ts']
    plt.plot(t, tc, lw=2, label='Temp. Reading', color='#3884c9')
    plt.plot(t, tt, '--', lw=2, label='Temp. Threshold', color='#3884c9')
    if len(t) >= BUFFER_SIZE:
        # for clarity the smoothing and standard error computations are performed on both axis'
        # compute digital signal smoothing
        # plot mean convolution (digital signal smoothing)
        plt.plot(smooth(t, BUFFER_SIZE),
                 smooth(tc, BUFFER_SIZE),
                 'k-', lw=2, label=f'µ Convolve (Window Size: {BUFFER_SIZE})')
        # compute standard error (and mean)
        # truncating excess data with integer division
        # numpy if reshape size param -1 will choose that parameter based on data
        resample_tc = np.reshape(tc[:len(tc) // BUFFER_SIZE * BUFFER_SIZE], (-1, BUFFER_SIZE))
        resample_t = np.reshape(t[:len(t) // BUFFER_SIZE * BUFFER_SIZE], (-1, BUFFER_SIZE))
        # perform mean computation on the vertical axis
        plt.errorbar(np.mean(resample_t, axis=1),
                     np.mean(resample_tc, axis=1),
                     yerr=np.std(resample_tc, axis=1) / np.sqrt(BUFFER_SIZE),  # type: ignore
                     fmt=' ', lw=2, xerr=None, ecolor='r', capsize=5, label='Std. Error')
    if gp_low.any(): plt.plot(gp_low_t, gp_low, label='GPIO 4 Low',
                              marker="v", color='g', linestyle='None')
    if gp_high.any(): plt.plot(gp_high_t, gp_high, label='GPIO 4 High',
                               marker="^", color='r', linestyle='None')
    plt.legend()


plt.style.use('fivethirtyeight')
ani = FuncAnimation(plt.gcf(), animate, interval=1000)  # type: ignore
plt.tight_layout()
plt.show()
_log.info("Plot successfully created")
