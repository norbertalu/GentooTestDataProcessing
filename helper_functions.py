import numpy as np
def U_config_or_not(temp1, temp2):
    # Ensure that temp1 and temp2 are numpy arrays
    if not isinstance(temp1, np.ndarray):
        temp1 = np.array(temp1)
    if not isinstance(temp2, np.ndarray):
        temp2 = np.array(temp2)

    # Compare corresponding elements and return an array of 0s and 1s
    return (temp1 > temp2).astype(int)