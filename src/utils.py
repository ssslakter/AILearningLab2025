import torch
from tqdm.auto import tqdm
from numpy import average
from torcheval.metrics import MulticlassAccuracy, MulticlassPrecision, MulticlassRecall, MulticlassF1Score

def predict(model, dl):
    preds, targets = [], []
    with torch.no_grad():
        for batch in tqdm(dl):
            batch = batch.to(model.device)
            logits = model(**batch).logits
            preds.append(logits.argmax(dim=-1)) 
            targets.append(batch["labels"])
    
    preds = torch.cat(preds).detach().cpu()
    targets = torch.cat(targets).detach().cpu()        
    return preds, targets


def do_eval(model, dl, agg=False):
    preds, targets = predict(model, dl)
    average = None if not agg else 'micro'
    metric_classes = {
        "accuracy": MulticlassAccuracy,
        "precision": MulticlassPrecision,
        "recall": MulticlassRecall,
        "f1": MulticlassF1Score,
    }
    results = {}
    for metric_name, metric_cls in metric_classes.items():
        # Create a new metric object for each metric to avoid state sharing
        metric_obj = metric_cls(average=average, num_classes=3)
        metric_obj.update(preds, targets)
        if not agg:
            results[metric_name] = {model.config.id2label[i]: v.item() for i, v in enumerate(metric_obj.compute())}
        else:
            results[metric_name] = metric_obj.compute().item()
    return results