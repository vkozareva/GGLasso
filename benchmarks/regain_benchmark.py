import numpy as np
import itertools
import time

from tqdm import trange

from regain.covariance import GraphicalLasso as rg_GL

from benchmarks.utilita import benchmark_parameters, save_dict, load_dict


def regain_time(X=np.array([]), Z=dict, rg_params=dict, lambda_list=list, n_iter=int, warm_start=False, max_iter=50000):
    
    precision_dict = dict()
    time_dict = dict()
    accuracy_dict = dict()

    tol_list = rg_params["tol"]
    rtol_list = rg_params["rtol"]
    
    p = X.shape[1]
    N = X.shape[0]

    for tol, rtol in itertools.product(tol_list, rtol_list):

        addon_time = 0.
        Omega_0 = np.eye(X.shape[1])
        for l1 in lambda_list:

            key = "regain" + "_tol_" + str(tol) + "_rtol_" + str(rtol) + "_p_" + str(p) + "_N_" + str(N)  + "_l1_" + str(l1)
            
            time_list = list()
            for _ in trange(n_iter, desc=key, leave=True):
                start = time.perf_counter()
                model = rg_GL(alpha=l1, tol=tol, rtol=rtol, max_iter=max_iter,
                              assume_centered=False, init=Omega_0, verbose=False)
                Z_i = model.fit(X)
                end = time.perf_counter()

                time_list.append(end - start)

                
            time_dict[key] = np.mean(time_list) + addon_time
            
            if warm_start:
                Omega_0 = Z_i.precision_
                addon_time += np.mean(time_list)

            precision_dict[key] = Z_i.precision_

            model_key = "p_" + str(p) + "_N_" + str(N) + "_l1_" + str(l1)
            accuracy = np.linalg.norm(Z[model_key] - np.array(Z_i.precision_)) / np.linalg.norm(Z[model_key])
            accuracy_dict[key] = accuracy


    return time_dict, accuracy_dict, precision_dict


def run_regain(X_dict=dict, S_dict=dict, model_Z_dict=dict, lambda_list=list, n_iter=int, regain_params=dict):
    time_dict = dict()
    accuracy_dict = dict()
    Z_dict = dict()
    trace_dict = dict()

    for X, S in zip(list(X_dict.values()), list(S_dict.values())):
        rg_time, rg_accuracy, Z_rg = regain_time(X=X, Z=model_Z_dict, rg_params=regain_params,
                                                 lambda_list=lambda_list, n_iter=n_iter)

        time_dict.update(rg_time)
        accuracy_dict.update(rg_accuracy)
        Z_dict.update(Z_rg)

        for key, item in Z_dict.items():
            trace_dict.update({key: {"Z": item, "X": X, "S": S}})

    return time_dict, accuracy_dict, trace_dict


# Main entry point
if __name__ == "__main__":
    _, rg_params, _, lambda_list = benchmark_parameters()
    S_dict = load_dict(dict_name="S_dict")
    X_dict = load_dict(dict_name="X_dict")
    Z_dict = load_dict(dict_name="Z_dict")

    time_dict, accuracy_dict, trace_dict = run_regain(X_dict=X_dict, S_dict=S_dict, model_Z_dict=Z_dict,
                                                      lambda_list=lambda_list, n_iter=2, regain_params=rg_params)

    save_dict(D=time_dict, name="regain_time_dict")
    save_dict(D=accuracy_dict, name="regain_acc_dict")
    save_dict(D=trace_dict, name="regain_trace_dict")
