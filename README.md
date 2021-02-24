# ekpmeasure
Repository of computer control code for various experiments as well as some analysis code for importing data from various tools into python


## Example usage of FE_switching analysis:
---
```python
from ekpmeasure.analysis.FE_switching import dataset, grouped_dataset

path = 'some path'
dset = dataset(path)
dset.query("high_voltage_v == .5")
```

![alt text](./src/dataset.PNG?raw=true)

```python
meta_data = dset.query("high_voltage_v == .5 and delay_ns < 25").meta_data
data = grouped_dataset(path, meta_data = meta_data)
data
```

<p align="center">
  <img src="./src/grouped_dataset.PNG?raw=true" width="350" title="grouped_dataset">
</p>
![alt text](./src/grouped_dataset.PNG?raw=true)

```python
desired_index = 0
samples = data.get_data_for_group_index([desired_index])
samples[desired_index]
```
![alt text](./src/samples.PNG?raw=true)

```python
import matplotlib.pyplot as plt

fig, ax = plt.subplots(figsize = (8,6))

mean_samples = samples.mean()
for key in mean_samples:
    internal_dict = mean_samples[key]
    plt.plot(internal_dict['time'], internal_dict['p1'])

ax.tick_params(labelsize = 20)
ax.set_xlabel('Time (ns)', size = 20)
ax.set_ylabel('Voltage (V)', size = 20)
```

![alt text](./src/p1curve.PNG?raw=true)

---

### To-do 2/23/21
- add ferroelectric switching experimental analysis + operational control for tds6604 (higher speed scope)
- add requirements.txt 
- add install instructions  
