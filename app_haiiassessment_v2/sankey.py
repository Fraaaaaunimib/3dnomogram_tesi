
# import pandas as pd
# import numpy as np
import plotly.graph_objects as go
import uuid
import itertools
import pandas as pd
# import plotly.io as pio

# file_path_ALL_code = glob.glob('/content/drive/My Drive/**/ALL-code.csv', recursive=True)[0]
# df_ALL_code = pd.read_csv(file_path_ALL_code)

def count_paths(df):
  # Combine the columns to represent the paths
  df['path'] = df['HD1'].astype(str) + df['AI'].astype(str) + df['FHD'].astype(str)

  # Count occurrences of each path
  path_counts = df.groupby('path').size().reset_index(name='count')
  path_counts = path_counts.sort_values(by='path')

  return path_counts

def check_missing_paths(path_counts):
    """
    Checks for the presence of all possible paths (000, 001, ..., 111) in the given path counts.

    Args:
        path_counts (pd.DataFrame): DataFrame with 'path' and 'count' columns.

    Returns:
        list: A list of missing paths.
    """
    all_paths = [''.join(p) for p in itertools.product('01', repeat=3)]
    present_paths = set(path_counts['path'])
    missing_paths = [path for path in all_paths if path not in present_paths]
    return missing_paths


def sankey(df_ALL_code):

    # NEW
    for col in ['HD1', 'AI', 'FHD']:
        df_ALL_code[col] = pd.to_numeric(df_ALL_code[col], errors='coerce').astype('Int64')
    path_counts = count_paths(df_ALL_code)
    missing = check_missing_paths(path_counts)
    # missing
    flag = []

    for i in missing:
      path_counts = pd.concat([path_counts, pd.DataFrame({'path': [i], 'count': [1]})], ignore_index=True) #[0]
      flag.append(i)

    path_counts = path_counts.sort_values(by='path')
    path_counts_list = path_counts['count'].tolist()

    combination_counts = df_ALL_code.groupby(['HD1', 'AI', 'FHD']).size().reset_index(name='count')
    # fp = combination_counts['count'].tolist() # final_paths_counts_list
    fp = path_counts_list
    sum_hd1_0 = combination_counts[combination_counts['HD1'] == 0]['count'].sum()
    sum_hd1_1 = combination_counts[combination_counts['HD1'] == 1]['count'].sum()

    sum_hd1_0_ai_0 = combination_counts[(combination_counts['HD1'] == 0) & (combination_counts['AI'] == 0)]['count'].sum()
    sum_hd1_0_ai_1 = combination_counts[(combination_counts['HD1'] == 0) & (combination_counts['AI'] == 1)]['count'].sum()
    sum_hd1_1_ai_0 = combination_counts[(combination_counts['HD1'] == 1) & (combination_counts['AI'] == 0)]['count'].sum()
    sum_hd1_1_ai_1 = combination_counts[(combination_counts['HD1'] == 1) & (combination_counts['AI'] == 1)]['count'].sum()

    for i in [sum_hd1_0_ai_0, sum_hd1_0_ai_1, sum_hd1_1_ai_0, sum_hd1_1_ai_1]:
      print(i)
    print(fp)

    cnl = [sum_hd1_0_ai_0, sum_hd1_0_ai_1, sum_hd1_1_ai_0, sum_hd1_1_ai_1]

    # y position
    y_hd_0_ai_0 = 0.1
    y_hd_0_ai_1 = 0.1+((cnl[0]/sum_hd1_0)*0.5)
    y_hd_1_ai_0 = 0.9-((cnl[3]/sum_hd1_1)*0.5)
    y_hd_1_ai_1 = 0.9

    total_count = sum(fp)
    prop_final = [x/total_count for x in fp]
    for i in range(len(prop_final)):
      if prop_final[i]==0:
        prop_final[i] = 0.005
    print(prop_final)
    y_000 = 0.05
    # y_001 = (y_000 + prop_final[0]/2 + 0.05)
    y_001 = (y_000 + prop_final[0]/2 + 0.01)
    # y_002 = (y_001 + prop_final[1]/2+ 0.05)
    y_002 = (y_001 + prop_final[1]/2+ 0.06)
    y_003 = (y_002 + prop_final[2]/2 + 0.05)

    y_007 = 0.95
    # y_006 = (y_007 - prop_final[7]/2 - 0.05)
    y_006 = (y_007 - prop_final[7]/2 + 0.05)
    # y_005 = (y_006 - prop_final[6]/2 - 0.05)
    y_005 = (y_006 - prop_final[6]/2 - 0.1)
    # y_004 = (y_005 - prop_final[5]/2 - 0.05)
    y_004 = (y_005 - prop_final[5]/2 - 0.05)

    # from IPython import get_ipython
    # from IPython.display import display

    data = go.Sankey(
        type="sankey",
        orientation="h",
        node=dict(
            pad=15,
            thickness=20,
            line=dict(color="black", width=0.5),
            label=[
                f"",
                f"",
                f"00 ({sum_hd1_0_ai_0} - {sum_hd1_0_ai_0/total_count:.2%})",
                f"01 ({sum_hd1_0_ai_1} - {sum_hd1_0_ai_1/total_count:.2%})",
                f"10 ({sum_hd1_1_ai_0} - {sum_hd1_1_ai_0/total_count:.2%})",
                f"11 ({sum_hd1_1_ai_1} - {sum_hd1_1_ai_1/total_count:.2%})",
                f"",
                f"",
                f"",
                f"",
                f"",
                f"",
                f"",
                f""
            ],
            x=[0.1, 0.1, 0.4, 0.4, 0.4, 0.4, 0.7, 0.7, 0.7, 0.7, 0.7, 0.7, 0.7, 0.7],
            y=[y_hd_0_ai_0, y_hd_1_ai_1, y_hd_0_ai_0, y_hd_0_ai_1, y_hd_1_ai_0, y_hd_1_ai_1,
               y_000, y_001, y_002, y_003, y_004, y_005, y_006, y_007]
        ),
        link=dict(
            source=[0, 0, 1, 1, 2, 2, 3, 3, 4, 4, 5, 5],
            target=[2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13],
            value=[sum_hd1_0_ai_0, sum_hd1_0_ai_1, sum_hd1_1_ai_0, sum_hd1_1_ai_1,
                   fp[0], fp[1], fp[2], fp[3], fp[4], fp[5], fp[6], fp[7]],
            color='lightgrey'  # link color to lightgrey

        )
    )


    # mapping between node index and desired color
    node_color_map = {
        0: "#FD3216",  # Node 0
        1: "#00B5F7",
        2: "#FD3216",
        3: "#00B5F7",
        4: "#FD3216",
        5: "#00B5F7",
        6: "#FD3216",
        7: "#00B5F7",
        8: "#FD3216",
        9: "#00B5F7",
        10: "#FD3216",
        11: "#00B5F7",
        12: "#FD3216",
        13: "#00B5F7"
    }


    # Get the color for each node based on its index
    node_colors = [node_color_map[i] for i in range(len(data['node']['label']))]
    data.update(node=dict(color=node_colors))


    layout = go.Layout(
        title="Sankey Diagram: HD1 -> AI -> FHD",
        font=dict(size=10),
        annotations=[
            dict(
                x=0.1,
                y=1.1,
                text="HD1",
                showarrow=False,
                font=dict(size=14)
            ),
            dict(
                x=0.4,
                y=1.1,
                text="HD1-AI",
                showarrow=False,
                font=dict(size=14)
            ),
            dict(
                x=0.7,
                y=1.1,
                text="HD1-AI-FHD",
                showarrow=False,
                font=dict(size=14)
            ),
            dict(
                x = 0.72,
                y = 1- y_000 + 0.025,
                xanchor='left',
                text=f"000 \n(0 - {0:.2%})" if '000' in flag else f"000 \n({fp[0]} - {fp[0]/total_count:.2%})",
                # text=f"000 \n({fp[0]} - {fp[0]/total_count:.2%})",
                showarrow=False,
                font=dict(size=10)
            ),
            dict(
                x = 0.72,
                y = 1- y_002 + 0.025,
                xanchor='left',
                text=f"010 \n(0 - {0:.2%})" if '010' in flag else f"010 \n({fp[2]} - {fp[2]/total_count:.2%})",
                # text=f"010 \n({fp[2]} - {fp[2]/total_count:.2%})",
                showarrow=False,
                font=dict(size=10)
            ),
            dict(
                x = 0.72,
                y = 1- y_003 + 0.025,
                xanchor='left',
                text=f"011 \n(0 - {0:.2%})" if '011' in flag else f"011 \n({fp[3]} - {fp[3]/total_count:.2%})",
                #text=f"011 \n({fp[3]} - {fp[3]/total_count:.2%})",
                showarrow=False,
                font=dict(size=10)
            ),
            dict(
                x = 0.72,
                y = 1- y_004 + 0.005,
                xanchor='left',
                text=f"100 \n(0 - {0:.2%})" if '100' in flag else f"100 \n({fp[4]} - {fp[4]/total_count:.2%})",
                #text=f"100 \n({fp[4]} - {fp[4]/total_count:.2%})",
                showarrow=False,
                font=dict(size=10)
            ),
            dict(
                x = 0.72,
                y = 1- y_005 + 0.005,
                xanchor='left',
                text=f"101 \n(0 - {0:.2%})" if '101' in flag else f"101 \n({fp[5]} - {fp[5]/total_count:.2%})",
                #text=f"101 \n({fp[5]} - {fp[5]/total_count:.2%})",
                showarrow=False,
                font=dict(size=10)
            ),
            dict(
                x = 0.72,
                y = 1- y_007 + 0.005,
                xanchor='left',
                text=f"111 \n(0 - {0:.2%})" if '111' in flag else f"111 \n({fp[7]} - {fp[7]/total_count:.2%})",
                #text=f"111 \n({fp[7]} - {fp[7]/total_count:.2%})",
                showarrow=False,
                font=dict(size=10)
            ),
            dict(
                x= 0.1 - 0.02,
                y=1 - y_hd_0_ai_0 + 0.025,
                xanchor='right',
                text=f"0 ({sum_hd1_0} - {sum_hd1_0/total_count:.2%})",
                showarrow=False,
                font=dict(size=10)
            ),
            dict(
                x= 0.1 - 0.02,
                y=1 - y_hd_1_ai_1 + 0.025,
                xanchor='right',
                text=f"1 ({sum_hd1_1} - {sum_hd1_1/total_count:.2%})",
                showarrow=False,
                font=dict(size=10)
            ),
            dict(
                x = 0.72,
                y = 1- y_006 - 0.02,
                xanchor='left',
                text=f"110 \n(0 - {0:.2%})" if '110' in flag else f"110 \n({fp[6]} - {fp[6]/total_count:.2%})",
                showarrow=False,
                font=dict(size=10)
            ),
            dict(
                x = 0.72,
                y = 1- y_001 + 0.0275,
                xanchor='left',
                text=f"001 \n(0 - {0:.2%})" if '001' in flag else f"001 \n({fp[1]} - {fp[1]/total_count:.2%})",
                # text=f"001 \n({fp[1]} - {fp[1]/total_count:.2%})",
                showarrow=False,
                font=dict(size=10)
            ),
        ]
    )

    fig = go.Figure(data=[data], layout=layout)


    #OLD
    # fig.show()
    id = str(uuid.uuid4())
    filename =  "output3/" + id + "_sankey" + ".png"
    path = "static/" + filename

    #plt.savefig(path, dpi=300, bbox_inches="tight")
    #fig.to_image(format="png", width=600, height=350, scale=2)
    #fig.write_image(path=path)
    fig.write_image(path, format="png", scale=2) # 300 DPI equivalent

    return filename

