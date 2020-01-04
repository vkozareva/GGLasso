"""
author: Fabian Schaipp
"""

import numpy as np
import time

from ..helper.basic_linalg import trp
from .ggl_helper import prox_p, phiplus, prox_od_1norm, prox_od_2norm


def latent_ADMM_GGL(S, lambda1, lambda2, mu1, mu2, R_0, \
             n_samples = None, eps_admm = 1e-5 , verbose = False, measure = False, **kwargs):
    """
    This is an ADMM algorithm for solving the Group Graphical Lasso problem with Latent Variables
    
    n_samples are the sample sizes for the K instances, can also be None or integer
    max_iter and rho can be specified via kwargs
    X0,X1,X2 denote the dual varibales
    Z and W denote the additional variables from reformulation
    """
    assert R_0.shape == S.shape
    assert S.shape[1] == S.shape[2]
    
    (K,p,p) = S.shape
    
    if 'max_iter' not in kwargs.items():
        max_iter = 1000
    if 'rho' not in kwargs.items():
        rho = 1
    
    # n_samples None --> set them all to 1
    # n_samples integer --> all instances have same number of samples
    # else --> n_samples should be array with sample sizes
    if n_samples == None:
        nk = np.ones((K,1,1))
    elif type(n_samples) == int:
        nk = n_samples * np.ones((K,1,1)) 
    else:
        assert len(nk) == K
        nk = n_samples.reshape(K,1,1)
    
    # initialize 
    status = 'not optimal'
    R_t = R_0.copy()
        
    Theta_t = np.zeros((K,p,p))
    L_t = np.zeros((K,p,p))
    X0_t = np.zeros((K,p,p))
    X1_t = np.zeros((K,p,p))
    X2_t = np.zeros((K,p,p))
    Z_t = np.zeros((K,p,p))
    W_t = np.zeros((K,p,p))
    
    runtime = np.zeros(max_iter)
    kkt_residual = np.zeros(max_iter)
    
    for iter_t in np.arange(max_iter):
        
        # R step
        A_t = Theta_t - L_t + X0_t
        V_t = (A_t + trp(A_t))/2 - (1/rho) * S
        eigD, eigQ = np.linalg.eigh(V_t) 
        for k in np.arange(K):
            R_t[k,:,:] = phiplus(V_t, 1/rho, D = eigD[k,:], Q = eigQ[k,:,:])
            
        # Theta step
        B_t = (R_t + L_t - X0_t  + Z_t - X1_t) / 2
        Theta_t = prox_od_1norm(B_t, lambda1/(2*rho))
        
        # L step
        C_t = (X0_t + Theta_t - R_t + W_t - X2_t) / 2
        
        # Z step
        Z_t = prox_od_2norm(Theta_t + X1_t, lambda2/rho)
        
        # W step
        W_t = prox_od_2norm(L_t + X2_t, mu2/rho)
        
        
        
        
    return
                
            
            
            
                
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        