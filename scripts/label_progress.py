"""Show labelling progress: how much of the chart's streams are labelled, and what's next."""

import pandas as pd

from greekrap.labels import load_labels

labels = load_labels("labels/artists.csv")
streams = pd.to_numeric(labels["streams_total"].str.replace(",", ""))   # in case the spreadsheet added commas

done = (labels["style"] != "") | (labels["role"] == "producer")   # producers count as handled
covered = 100 * streams[done].sum() / streams.sum()

print(f"{done.sum()} of {len(labels)} names labelled, covering {covered:.1f}% of artist-credited streams\n")
print(labels.loc[done, "style"].replace("", "(producer)").value_counts().to_string())
print("\nNext 10 to label:", labels.loc[~done, "name"].head(10).tolist())
