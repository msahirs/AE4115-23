n_elev = 4;
n_p_config =3;
n_fs = 3;
n_J = 4;
n_aoa = 4;

cand_set = [n_aoa n_J n_fs n_p_config n_elev];

full_fact_space = fullfact(cand_set);
candexch(full_fact_space,120)