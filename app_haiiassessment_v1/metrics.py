import numpy as np
import pandas as pd
import scipy.stats as stats
from scipy.stats import levene, mannwhitneyu, ttest_ind, ansari, iqr, norm
from sklearn.metrics import cohen_kappa_score

def safe_cohen_kappa(y1, y2):
    try:
        unique_y1 = np.unique(y1)
        unique_y2 = np.unique(y2)

        if len(unique_y1) == 1 or len(unique_y2) == 1:
            print(f"ATTENZIONE: Una delle due colonne è costante (y1={unique_y1}, y2={unique_y2})")
            return 0.0  # Se una colonna è costante, restituiamo 0

        score = cohen_kappa_score(y1, y2)
        return score if not np.isnan(score) else 0.0  # Se il valore è NaN, restituiamo 0.0
    except ValueError as e:
        print(f"Errore in cohen_kappa_score: {e}")
        return 0.0  # In caso di errore, restituiamo 0.0

def safe_divide(numerator, denominator, epsilon=1e-10):
    return numerator / (denominator if denominator != 0 else epsilon)

def safe_value(value, default=0.0):
    """Restituisce il valore se è valido, altrimenti un valore predefinito (default)."""
    return value if not np.isnan(value) and np.isfinite(value) else default


def compute_effects_conf(data_in):

    data = data_in.copy()

    acc_pre = data.groupby("id")["C1"].mean()
    acc_post = data.groupby("id")["FC"].mean()

    q25 = np.quantile(acc_pre, 0.25)
    q75 = np.quantile(acc_pre, 0.75)
    data["Type_H2"] = "Others"
    data.loc[data["id"].isin(acc_pre[acc_pre <= q25].index), "Type_H2"] = "Low confident"
    data.loc[data["id"].isin(acc_pre[acc_pre >= q75].index), "Type_H2"] = "High confident"

    var_dec = 1-ansari(acc_pre, acc_post, alternative="greater").pvalue

    acc_low_pre = data[data["Type_H2"] == "Low confident"].groupby("id")["C1"].mean().values
    acc_low_post = data[data["Type_H2"] == "Low confident"].groupby("id")["FC"].mean().values
    acc_low = 1-mannwhitneyu(acc_low_pre, acc_low_post, alternative="less").pvalue

    acc_all = 1-mannwhitneyu(acc_pre, acc_post, alternative="less").pvalue
    var_eq = ansari(acc_pre, acc_post).pvalue

    acc_hi_pre = data[data["Type_H2"] == "High confident"].groupby("id")["C1"].mean().values
    acc_hi_post = data[data["Type_H2"] == "High confident"].groupby("id")["FC"].mean().values
    acc_high = 1-mannwhitneyu(acc_hi_pre, acc_hi_post, alternative="less").pvalue
    var_inc = 1-ansari(acc_pre, acc_post, alternative="less").pvalue

    ai_effect_on_confidence = (acc_post.median() - acc_pre.median())/ iqr(acc_pre)
    nnd_confidence = (1/(2*stats.norm.cdf(ai_effect_on_confidence/np.sqrt(2), loc=0, scale=1)-1))
    leveler_confidence =(1/(1/(2*var_dec) + 1/(2*acc_low)))
    escalator_confidence = (1/(1/(2*var_eq) + 1/(2*acc_all)))
    slingshot_confidence =(1/(1/(2*var_inc) + 1/(2*acc_high)))
    tarpit_confidence = mannwhitneyu(acc_pre, acc_post, alternative="less").pvalue
    dominance_strength_confidence = (data[data["FC"] != data["C1"]].shape[0]/data.shape[0])
    dominance_direction_confidence = (data[(data["FC"]  > data["C1"])].shape[0] - data[(data["FC"] < data["C1"])].shape[0])/data[data["FC"] != data["C1"]].shape[0]
    return ai_effect_on_confidence, nnd_confidence, leveler_confidence, escalator_confidence, slingshot_confidence, tarpit_confidence, dominance_strength_confidence, dominance_direction_confidence

def compute_effects(all_data):

    #all_data = pd.read_csv(filename)
    all_data = all_data.dropna()
    #data = data_in.copy()

    listTuple=[]

    for s in all_data["Study"].unique():

        data = all_data[(all_data["Study"] == s)].copy()

        acc_pre = data.groupby("id")["HD1"].mean()
        acc_post = data.groupby("id")["FHD"].mean()

        q25 = np.quantile(acc_pre, 0.25)
        q75 = np.quantile(acc_pre, 0.75)
        data["Type_H2"] = "Others"
        data.loc[data["id"].isin(acc_pre[acc_pre <= q25].index), "Type_H2"] = "Low performer"
        data.loc[data["id"].isin(acc_pre[acc_pre >= q75].index), "Type_H2"] = "High performer"

        acc_t_pre = (acc_pre - np.mean(acc_pre))**2
        acc_t_post = (acc_post - np.mean(acc_post))**2
        var_dec = 1-ttest_ind(acc_t_pre, acc_t_post, alternative="greater").pvalue

        acc_low_pre = data[data["Type_H2"] == "Low performer"].groupby("id")["HD1"].mean().values
        acc_low_post = data[data["Type_H2"] == "Low performer"].groupby("id")["FHD"].mean().values
        acc_low = 1-mannwhitneyu(acc_low_pre, acc_low_post, alternative="less").pvalue

        acc_all = 1-mannwhitneyu(acc_pre, acc_post, alternative="less").pvalue
        var_eq = levene(acc_pre, acc_post).pvalue

        acc_hi_pre = data[data["Type_H2"] == "High performer"].groupby("id")["HD1"].mean().values
        acc_hi_post = data[data["Type_H2"] == "High performer"].groupby("id")["FHD"].mean().values
        acc_high = 1-mannwhitneyu(acc_hi_pre, acc_hi_post, alternative="less").pvalue
        var_inc = 1-ttest_ind(acc_t_pre, acc_t_post, alternative="less").pvalue

        num = data[(data["HD1"] == 0) & (data["AI"] == 1) & (data["FHD"] == 1)].shape[0]
        num += data[(data["HD1"] == 1) & (data["AI"] == 0) & (data["FHD"] == 1)].shape[0]
        num += data[(data["HD1"] == 0) & (data["AI"] == 0) & (data["FHD"] == 1)].shape[0]

        if "C1" in data.columns and "FC" in data.columns:
            num += data[(data["HD1"] == 0) & (data["AI"] == 0) & (data["FHD"] == 0) & (data["C1"] > data["FC"])].shape[0]
            num += data[(data["HD1"] == 1) & (data["AI"] == 1) & (data["FHD"] == 1) & (data["C1"] < data["FC"])].shape[0]
        else:
            num += data[(data["HD1"] == 0) & (data["AI"] == 0) & (data["FHD"] == 0)].shape[0]*0.1
            num += data[(data["HD1"] == 1) & (data["AI"] == 1) & (data["FHD"] == 1)].shape[0]*0.2


        unique_ids = data['id'].unique()
        persuasion_values = np.zeros(len(unique_ids))

        # Calculate the metrics for each id
        for idx, unique_id in enumerate(unique_ids):
            subset = data[data['id'] == unique_id]

            # Step 2: Compute Krippendorff's alpha between HD1 and AI
            hd1_ai_alpha = cohen_kappa_score(subset['HD1'], subset['AI'])

            # Step 3: Compute Krippendorff's alpha between FHD and AI
            fhd_ai_alpha = cohen_kappa_score(subset['FHD'], subset['AI'])

            # Step 4: Compute the delta
            delta = fhd_ai_alpha - hd1_ai_alpha

            # Step 5: Compute the persuasion value
            persuasion_values[idx] = delta

        # Round results to three decimal places
        persuasion_values = persuasion_values
        average_persuasion_value = np.nanmean(persuasion_values)
        std_dev_persuasion_values = np.nanstd(persuasion_values)

        appropriate_reliance = num/data.shape[0]
        deference_strength = (data[(data["FHD"] != data["HD1"]) & (data["FHD"] == data["AI"])].shape[0]/data[data["HD1"] != data["AI"]].shape[0])
        deference_direction = ((data[(data["FHD"] != data["HD1"]) & (data["FHD"] == data["AI"]) & (data["AI"] == 1 )].shape[0]) - (data[(data["FHD"] != data["HD1"]) & (data["FHD"] == data["AI"]) & (data["AI"] == 0 )].shape[0]))/ (data[(data["FHD"] != data["HD1"]) & (data["FHD"] == data["AI"])]).shape[0]
        dominance_strength = (data[data["FHD"] != data["HD1"]].shape[0]/data.shape[0])
        dominance_direction = (data[(data["FHD"] == 1) & (data["HD1"] == 0)].shape[0] - data[(data["FHD"] == 0) & (data["HD1"] == 1)].shape[0])/data[data["FHD"] != data["HD1"]].shape[0]
        ai_effect_on_decision = (acc_post.mean() - acc_pre.mean())/ acc_pre.std()
        nnd = 1/(2*stats.norm.cdf(ai_effect_on_decision/np.sqrt(2), loc=0, scale=1)-1)
        leveler = (1/(1/(2*var_dec) + 1/(2*acc_low)))
        escalator = (1/(1/(2*var_eq) + 1/(2*acc_all)))
        slingshot = (1/(1/(2*var_inc) + 1/(2*acc_high)))
        tarpit = mannwhitneyu(acc_pre, acc_post, alternative="less").pvalue

        determination_strength = safe_divide(
            data[(data["FHD"] == data["HD1"]) & (data["FHD"] != data["AI"])].shape[0],
            data[data["HD1"] != data["AI"]].shape[0]
            #data.shape[0]
        )

        determination_direction = safe_divide(
            data[(data["FHD"] == data["HD1"]) & (data["FHD"] != data["AI"]) & (data["AI"] == 1)].shape[0] -
            data[(data["FHD"] == data["HD1"]) & (data["FHD"] != data["AI"]) & (data["AI"] == 0)].shape[0],
            data[(data["FHD"] == data["HD1"]) & (data["FHD"] != data["AI"])].shape[0]
        )

        rair = safe_divide(
            data[(data["FHD"] == 1) & (data["HD1"] == 0) & (data["AI"] == 1)].shape[0],
            data[(data["FHD"] == 1) & (data["HD1"] == 0) & (data["AI"] == 1)].shape[0] +
            data[(data["FHD"] == 0) & (data["HD1"] == 0) & (data["AI"] == 1)].shape[0]
        )

        rsr = safe_divide(
            data[(data["FHD"] == 1) & (data["HD1"] == 1) & (data["AI"] == 0)].shape[0],
            data[(data["FHD"] == 1) & (data["HD1"] == 1) & (data["AI"] == 0)].shape[0] +
            data[(data["FHD"] == 0) & (data["HD1"] == 1) & (data["AI"] == 0)].shape[0]
        )

        acc_h = np.mean(acc_pre)
        acc_ai = data["AI"].mean()
        exp_ar = (1 - acc_h) * acc_ai * acc_h + acc_h * acc_ai * acc_h * 0.5 + acc_h * (1 - acc_ai) * acc_h
        exp_ar += (1 - acc_h) * (1 - acc_ai) * acc_h + (1 - acc_h) * (1 - acc_ai) * (1 - acc_h) * 0.5

        appr_inf = 1 - safe_divide(1 - appropriate_reliance, 1 - exp_ar)

        dictionary = {"study":s,
                "appropriate reliance": appropriate_reliance,
                "appropriate influence": appr_inf,
                "ai effect on decision": ai_effect_on_decision,
                "nnd": nnd,
                "leveler": leveler,
                "escalator": escalator,
                "slingshot": slingshot,
                "tarpit": tarpit,
                "dominance strength": dominance_strength,
                "dominance direction": dominance_direction,
                "deference strength": deference_strength,
                "deference direction": deference_direction,
                "determination strength": determination_strength,
                "determination direction": determination_direction,
                "persuasion_index": average_persuasion_value,
                "persuasion values": persuasion_values,
                "persuasion_std": std_dev_persuasion_values,
                "rair": rair,
                "rsr": rsr}

        dictionary_arrotondata = {}
        for key, value in dictionary.items():
        # Controlla se il valore è numerico
            if isinstance(value, (int, float)):
                # Arrotonda il valore a tre decimali e aggiungi alla nuova dictionary
                dictionary_arrotondata[key] = round(value, 3)
            else:
                # Se il valore non è numerico, aggiungilo direttamente alla nuova dictionary
                dictionary_arrotondata[key] = value
        listTuple.append(dictionary_arrotondata)


    return listTuple