from sklearn.metrics import classification_report, confusion_matrix, roc_auc_score

def evaluate_class(y_test, y_pred):

    auc=roc_auc_score(y_test, y_pred)
    conf=confusion_matrix(y_test, y_pred)
    clr = classification_report(y_test, y_pred,digits=4)

    print("AUC: ",auc)
    print("Confusion Matrix: \n",conf)
    print("Classification Report: \n",clr)

    return {
        "AUC": auc,
        "Confusion Matrix": conf,
        "Classification Report": clr,
    }


