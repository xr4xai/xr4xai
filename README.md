# XR4XAI

### Jake Looney and Andrew Lay
### Sponsored by Dr. Sai Swaminathan, Dr. Jian Huang, and Dr. Catherine Schuman

## Current instructions to run visualizer: 
 
Clone the [TENNLab bitbucket repo](https://bitbucket.org/neuromorphic-utk/framework/src/master/) (you may have to ask Dr. Schuman or Dr. Plank for permission).
Then, you'll have to have to follow the instructions in `markdown/python.md` to get the Python API. This should require running `bash scripts/create_env.sh` to 
create a virtual environment `pyframework`. Then, you'll need to find the path of the pyframework (something akin to `source ~/framework/pyframework/bin/activate`)
it to the environment to `.neuro.env` in this directory with the variable name `FRAME_WORK`
i.e. `FRAME_WORK=<neuromorphic framework venv file>`
Then, doing `source start` will source you into the framework and install all the needed pyqt packages.
Finally, run `python3 graphics/qt_main.py` to start the current visualizer.

All together, that is:
- Create pyframework
- Create file `.neuro.env`
- Add the line `FRAME_WORK=<neuromorphic framework venv file>`
- `source start`
- `python3 ./graphics/qt_main.py`
