import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import uuid

def stacked(df_ALL_code):

    combination_counts = df_ALL_code.groupby(['HD1', 'AI', 'FHD']).size().reset_index(name='count')
    counts_list = combination_counts['count'].tolist()

    # Create proportions (percentages) and prepare data for the plot
    keys = ['000', '001', '010', '011', '100', '101', '110', '111']
    new_data = dict(zip(keys, counts_list))

    total = sum(new_data.values())
    proportions = {key: value / total * 100 for key, value in new_data.items()}

    # Data dictionary
    data = {
        'Category': [f"{key} ({value})" for key, value in new_data.items()],
        'Percentage': list(proportions.values())
    }

    colors = ['#F98890', '#41B2D8', '#FFC950', '#53C6B3', '#9459D8', '#FFA347', '#C5C5C5', '#9662C6']

    # Convert dictionary to pandas DF
    df = pd.DataFrame(data)
    df['Cumulative_Percentage'] = np.cumsum(df['Percentage'])

    fig, ax = plt.subplots(figsize=(20, 2))

    bar_width = 0.8
    y_position = 0
    left = 0
    bars = []

    # Plot bars
    for i, row in df.iterrows():
        bar = ax.barh(y_position, row['Percentage'], height=bar_width, left=left, color=colors[i], label=row['Category'])
        bars.append(bar[0])
        left += row['Percentage']

    ax.set_xlabel('Proportion (%)')
    ax.set_title('100% Stacked Horizontal Bar Chart for All Patterns')

    ax.set_yticks([])
    ax.set_yticklabels([])

    ax.set_xticks(range(0, 101, 10))
    ax.set_xlim(0, 100)

    ax.legend(bbox_to_anchor=(1.05, 1), loc='upper left')

    # Show annotations when the cursor moves
    annot = ax.annotate("", xy=(0, 0), xytext=(-20, 10), textcoords="offset points",
                        bbox=dict(boxstyle="square", fc="w"),
                        arrowprops=None)
    annot.set_visible(False)


    def update_annot(event):
        """Update annotation on cursor position."""
        vis = annot.get_visible()
        for bar, row in zip(bars, df.itertuples()):
            cont, ind = bar.contains(event)
            if cont:
                annot.xy = (event.xdata, event.ydata)
                annot.set_text(f"{row.Category}\n{row.Percentage:.2f}%")
                annot.get_bbox_patch().set_alpha(0.4)
                annot.set_visible(True)
                fig.canvas.draw_idle()
                return
        if vis:
            annot.set_visible(False)
            fig.canvas.draw_idle()

    fig.canvas.mpl_connect("motion_notify_event", update_annot)

    # plt.show()
    id = str(uuid.uuid4())
    filename = "output3/" + id + "_stacked" + ".png"
    path = "static/" + filename
    plt.savefig(path, dpi=300, bbox_inches="tight")

    return filename
