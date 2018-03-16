#Last Updated: 8/26/17
import multiprocessing
import warnings
import DataModel
import utils
import teamCalcDataKeysToLambda as calcs

#Process for calculating data from individual TIMD
class FirstTIMDProcess(multiprocessing.Process):
    def __init__(self, timd, calculatedTIMDsList, calculator):
        super(FirstTIMDProcess, self).__init__()
        self.timd = timd
        self.calculatedTIMDsList = calculatedTIMDsList
        self.calculator = calculator
        warnings.simplefilter('error', RuntimeWarning)
    
    #Does calculations if complete, otherwise doesn't, and adds TIMD to list of used TIMDs
    def run(self):
        if not self.calculator.su.timdIsCompleted(self.timd):
            print('> TIMD is not complete for team ' + str(self.timd.teamNumber) + ' in match ' + str(self.timd.matchNumber))
            self.calculatedTIMDsList.append(self.timd)
        else:
            print('> Beginning first calculations for team ' + str(self.timd.teamNumber) + ' in match ' + str(self.timd.matchNumber))
            calcs.TIMDCalcDict(self.timd, self.calculator)
            self.calculatedTIMDsList.append(self.timd)
            self.calculator.calcTIMDs.append(self.timd)
