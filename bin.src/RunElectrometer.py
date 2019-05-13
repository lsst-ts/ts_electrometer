from lsst.ts.electrometer.electrometerCSC.ElectrometerCSC import ElectrometerCsc
import lsst.ts.salobj as salobj
import SALPY_Electrometer
import argparse

version=0.10

def create_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument("index", default=1, type=int)
    return parser

if __name__ == "__main__":
    parser = create_parser()
    args = parser.parse_args()
    print(args.index)
    ElectrometerCsc.main(index=args.index)
