# from flask import Flask, render_template, request, flash
# import pandas as pd
import uuid
import matplotlib.pyplot as plt
# import seaborn as sns
# from werkzeug.utils import secure_filename
# import os
import numpy as np


def single_paired(all_data, type_ai=None, group_user=None, sub=None, sub_vals=[], ai_level=None, savename="plot", palette=None, measure="Accuracy"):

    if "Type_AI" not in all_data.columns:
        all_data["Type_AI"] = ""

    if "Study" not in all_data.columns:
        all_data["Study"] = ""

    if type_ai is not None:
        all_data = all_data[all_data["Type_AI"] == type_ai]

    if sub is not None:
        all_data = all_data[all_data[sub].isin(sub_vals)]

    diagrams = []
    diagrams_list = [] # storing the plots
    effects = [
        "lifted", "repulsed", "outperformers", "ballasted", "spurred",
        "overcome", "empowered", "undermined", "unaffected"
    ]

    # Default palette if none is provided
    default_palette = {
        "Low performer": "blue",
        "High performer": "orange",
        "Others": "green"
    }

    for effect in effects:
        for s in all_data["Study"].unique():
            for t in all_data[all_data["Study"] == s]["Type_AI"].unique():
                data = all_data[(all_data["Type_AI"] == t) & (all_data["Study"] == s)].copy()
                if ai_level is None and "AI" in data.columns:
                    ai_level = data["AI"].mean()

                # Categorize performance levels
                accs = data.groupby("id")["HD1"].mean()
                q25 = np.quantile(accs, 0.25)
                q75 = np.quantile(accs, 0.75)
                data["Type_H"] = "Others"
                data.loc[data["id"].isin(accs[accs <= q25].index), "Type_H"] = "Low performer"
                data.loc[data["id"].isin(accs[accs >= q75].index), "Type_H"] = "High performer"

                # Calculate pre- and post-AI accuracies
                acc_pre = data.groupby("id")["HD1"].mean()
                acc_post = data.groupby("id")["FHD"].mean()
                diff = acc_post - acc_pre

                # Filter data based on the current effect
                if ai_level is not None:
                    effect_filter = {
                        "lifted": (diff > 0) & (acc_post < ai_level),
                        "repulsed": (diff < 0) & (acc_pre < ai_level),
                        "outperformers": (diff > 0) & (acc_post >= ai_level) & (acc_pre < ai_level),
                        "ballasted": (diff < 0) & (acc_pre >= ai_level) & (acc_post >= ai_level),
                        "spurred": (diff > 0) & (acc_pre >= ai_level),
                        "overcome": (diff < 0) & (acc_pre >= ai_level) & (acc_post < ai_level),
                        "empowered": (diff > 0),
                        "undermined": (diff < 0),
                        "unaffected": (diff == 0),
                    }
                    effect_mask = effect_filter[effect]
                    effect_data = data[data["id"].isin(acc_pre.index[effect_mask])]
                else:
                    effect_data = data

                # Create paired dot plot
                fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(8, 6), gridspec_kw={'width_ratios': [3, 1]})

                legend_labels = []
                legend_handles = []

                # Plot lines and scatter points for each performance group
                for performance_group in effect_data["Type_H"].unique():
                    group_data = effect_data[effect_data["Type_H"] == performance_group]
                    group_ids = group_data["id"].unique()
                    count = len(group_ids)
                    x1 = 0 + 0.1 * np.random.rand(len(group_ids))
                    x2 = 1 + 0.1 * np.random.rand(len(group_ids))

                    acc_pre_group = acc_pre[group_ids]
                    acc_post_group = acc_post[group_ids]

                    # Plot paired lines
                    ax1.plot([x1, x2], [acc_pre_group, acc_post_group], color="gray", alpha=0.5)

                    # Plot scatter points for pre- and post-AI
                    scatter_pre = ax1.scatter(x1, acc_pre_group, color=default_palette[performance_group], alpha=0.7)
                    scatter_post = ax1.scatter(x2, acc_post_group, color=default_palette[performance_group], alpha=0.7)

                    # Add legend entry
                    # print(legend_labels)
                    if performance_group not in legend_labels:
                        legend_labels.append(performance_group)
                        legend_handles.append(scatter_pre)

                    # Mean diff and ci for error bars
                    diff_group = acc_post_group - acc_pre_group
                    mean_diff_group = np.mean(diff_group)
                    ci_group = 1.96 * np.std(diff_group) / np.sqrt(len(diff_group))

                    # Plot error bars
                    ax2.errorbar(
                        x=np.random.normal(loc=0.0, scale=0.1),
                        y=mean_diff_group,
                        yerr=ci_group,
                        fmt='o',
                        color=default_palette[performance_group],
                        capsize=5
                    )

                # Plot labels
                ax1.set_xticks([0, 1])
                ax1.set_xticklabels(['Pre-AI (HD1)', 'Post-AI (FHD)'])
                ax1.set_ylabel("Performance")
                ax1.set_title(f'{effect.capitalize()}: {s} ({t})')

                # AI level line
                if ai_level is not None:
                    ai_line = ax1.axhline(ai_level, color="black", linestyle="--", label="AI Level")

                    legend_handles.append(ai_line)
                    legend_labels.append("AI")

                else: ai_line = None

                # ax2 properties
                ax2.axhline(0, color="grey", linestyle="--")
                ax2.set_xlim(-1, 1)
                ax2.set_title("Mean Difference")
                ax2.set_xticks([])
                ax2.yaxis.tick_right()
                ax2.yaxis.set_label_position("right")

                # Legend
                ax1.legend(legend_handles,[f"{label} (n={len(effect_data[effect_data['Type_H'] == label]['id'].unique())})" if label != "AI" else label for label in legend_labels],loc='best', fontsize='small')
                plt.tight_layout()

                # Check if any performance group is present besides AI
                performance_groups_present = any(group in effect_data["Type_H"].unique() for group in ["High performer", "Low performer", "Others"])

                # Store and save plot only if performance groups are present
                if performance_groups_present:
                    diagrams_list.append(fig)

                    # Save plot to file
                    id = str(uuid.uuid4())
                    namefile = "output3/" + id + f"_{effect}_{s}_{t}_paired_dot_plot.png"
                    path = "static/" + namefile
                    diagrams.append(namefile)

                    # os.makedirs(os.path.dirname(path), exist_ok=True)
                    #plt.savefig(path)
                    plt.savefig(path, dpi=300, bbox_inches="tight")
                plt.close()

    return diagrams

    '''
            id = str(uuid.uuid4())
            namefile = "output3/" + id + savename + (sub_vals[0] if sub is not None else "") + " " + str(s) + " " + str(t) +"_paired.png"
            path = "static/" + namefile


            plt.savefig(path, dpi=300, bbox_inches="tight")
            diagrams.append(namefile)

    return diagrams
    '''
