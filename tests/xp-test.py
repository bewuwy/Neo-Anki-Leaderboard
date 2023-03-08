# change cwd to the parent directory of the script
import sys
sys.path.append("./src")

import xp


if __name__ == "__main__":
    print(xp.calc_xp(100, 0.5))
    
    
