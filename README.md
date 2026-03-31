# Crossparametric dependencies and SNA

Scripts and data from the paper:

> Longhin, M., S. Ghinoi, G. Sorge, A. Artioli & C. Guardiano. 2026. Crossparametric dependencies and Social Network Analysis. In ed. by Hartmann, S. et al., _The Evolution of Language: Proceedings of the 16th International Conference (EVOLANG XVI)_. Nijmegen: The Evolution of Language Conferences. DOI: 10.17617/2.3696655.

```bibtex
@inproceedings{NetworksEvolang2026,
  title = {Crossparametric dependencies and {{Social Network Analysis}}},
  booktitle = {The {{Evolution}} of {{Language}}: {{Proceedings}} of the 16th {{International Conference}} ({{EVOLANG XVI}})},
  author = {Longhin, Marco and Ghinoi, Stefano and Sorge, Gaia and Artioli, Andrea and Guardiano, Cristina},
  editor = {Hartmann, Stefan and Sibierska, Marta and Fröhlich, Marlen and Jadoul, Yannick and Josserand, Mathilde and Matzinger, Theresa and Mudd, Katie and Nölle, Jonas and Pleyer, Michael and Wacewicz, Sławomir and Żywiczyński, Przemysław},
  date = {2026},
  publisher = {The Evolution of Language Conferences},
  location = {Nijmegen},
  doi = {10.17617/2.3696655},
  annotation = {Presented at the main conference poster session of EVOLANG XVI, 7-10 April 2026, Plovdiv, Bulgaria}
}
```

This repository includes:

- **TableA_94_2025.xlsx**: lists of parameter states used to generate the networks

- **visualizer.py**: script that generates the networks (outputs `.html` files)

- **networks**: folder containing the network representing the dependency structure of the parameter system and the networks representing languages

- **betweenness.py** and **closeness.py**: scripts that compute pairwise network similarity and node centrality (output `similarity_betweenness.png` and `similarity_closeness.png`)

- **network similarity and node centrality**: folder containing the plots of similarity decay under node removal based on closeness and betweenness centrality

- **poster_networks.pdf**: poster presented at the main conference poster session of EVOLANG XVI