# -*- coding: utf-8 -*-
# Copyright (c) 2019 - 2020 Simon Kern
# Copyright (c) 2015 Holger Nahrstaedt

import os
import numpy as np
from datetime import datetime
# from numpy.testing import (assert_raises, run_module_suite,
#                            assert_equal, assert_allclose, assert_almost_equal)
import unittest
import pyedflib


class TestEdfReader(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        # data_dir = os.path.join(os.getcwd(), 'data')
        data_dir = os.path.join(os.path.dirname(__file__), 'data')
        cls.edf_data_file = os.path.join(data_dir, 'test_generator.edf')
        cls.bdf_broken_file = os.path.join(data_dir, 'tmp_broken_file.bdf')
        cls.bdf_accented_file = os.path.join(data_dir, u'tmp_file_áä\'üöß.bdf')
        cls.edf_subsecond = os.path.join(data_dir, u'test_subsecond.edf')
        cls.tmp_edf_file = os.path.join(data_dir, u'test_tmp_file.edf')

    @classmethod
    def tearDownClass(cls):
        data_dir = os.path.join(os.path.dirname(__file__), 'data')
        tmpfiles = [f for f in os.listdir(data_dir) if f.startswith('tmp')]
        for file in tmpfiles:
            try:
                os.remove(os.path.join(data_dir, file))
            except Exception as e:
                print(e)

    def test_EdfReader(self):
        try:
            f = pyedflib.EdfReader(self.edf_data_file)
        except IOError:
            print('cannot open', self.edf_data_file)
            return

        ann_index, ann_duration, ann_text = f.readAnnotations()
        np.testing.assert_almost_equal(ann_index[0], 0)
        np.testing.assert_almost_equal(ann_index[1], 600)

        np.testing.assert_equal(f.signals_in_file, 11)
        np.testing.assert_equal(f.datarecords_in_file, 600)

        for i in np.arange(11):
            np.testing.assert_almost_equal(f.getSampleFrequencies()[i], 200)
            np.testing.assert_equal(f.getNSamples()[i], 120000)
        np.testing.assert_equal(f.handle, 0)
        f.close()
        np.testing.assert_equal(f.handle, -1)

    def test_indexerrors_thrown(self):
        try:
            f = pyedflib.EdfReader(self.edf_data_file)
        except IOError:
            print('cannot open', self.edf_data_file)
            return

        funcs = ['getSampleFrequency', 'getLabel', 'getPrefilter', 'getPhysicalMaximum',
                 'getPhysicalMinimum', 'getDigitalMaximum', 'getDigitalMinimum',
                 'getTransducer', 'getPhysicalDimension', 'readSignal']
        for i in range(10):
            for func in funcs:
                getattr(f, func)(i)
            
        for i in [-1, 11]:
            for func in funcs:
                with self.assertRaises(IndexError, msg="f.{}({})".format(func, i)):
                    getattr(f, func)(i)
            
        f.close()

    def test_EdfReader_headerInfos(self):
        try:
            f = pyedflib.EdfReader(self.edf_data_file)
        except IOError:
            print('cannot open', self.edf_data_file)
            return
        datetimeSoll = datetime(2011,4,4,12,57,2)
        np.testing.assert_equal(f.getStartdatetime(),datetimeSoll)
        np.testing.assert_equal(f.getPatientCode(), 'abcxyz99')
        np.testing.assert_equal(f.getPatientName(), 'Hans Muller')
        np.testing.assert_equal(f.getGender(), 'Male')
        np.testing.assert_equal(f.getBirthdate(), '30 jun 1969')
        np.testing.assert_equal(f.getPatientAdditional(), 'patient')
        np.testing.assert_equal(f.getAdmincode(), 'Dr. X')
        np.testing.assert_equal(f.getTechnician(), 'Mr. Spotty')
        np.testing.assert_equal(f.getEquipment(), 'test generator')
        np.testing.assert_equal(f.getRecordingAdditional(), 'unit test file')
        np.testing.assert_equal(f.getFileDuration(), 600)
        fileHeader = f.getHeader()
        np.testing.assert_equal(fileHeader["patientname"], 'Hans Muller')
        f.close()

    def test_EdfReader_signalInfos(self):
        try:
            f = pyedflib.EdfReader(self.edf_data_file)
        except IOError:
            print('cannot open', self.edf_data_file)
            return
        np.testing.assert_equal(f.getSignalLabels()[0], 'squarewave')
        np.testing.assert_equal(f.getLabel(0), 'squarewave')
        np.testing.assert_equal(f.getPrefilter(0), 'pre1')
        np.testing.assert_equal(f.getTransducer(0), 'trans1')
        for i in np.arange(1,11):
            np.testing.assert_equal(f.getPhysicalDimension(i), 'uV')
            np.testing.assert_equal(f.getSampleFrequency(i), 200)
            np.testing.assert_equal(f.getSampleFrequencies()[i], 200)

        np.testing.assert_equal(f.getSignalLabels()[1], 'ramp')
        np.testing.assert_equal(f.getSignalLabels()[2], 'pulse')
        np.testing.assert_equal(f.getSignalLabels()[3], 'noise')
        np.testing.assert_equal(f.getSignalLabels()[4], 'sine 1 Hz')
        np.testing.assert_equal(f.getSignalLabels()[5], 'sine 8 Hz')
        np.testing.assert_equal(f.getSignalLabels()[6], 'sine 8.1777 Hz')
        np.testing.assert_equal(f.getSignalLabels()[7], 'sine 8.5 Hz')
        np.testing.assert_equal(f.getSignalLabels()[8], 'sine 15 Hz')
        np.testing.assert_equal(f.getSignalLabels()[9], 'sine 17 Hz')
        np.testing.assert_equal(f.getSignalLabels()[10], 'sine 50 Hz')
        # testing file info and file_info_log
        f.file_info()
        f.file_info_long()
        f.close()

    def test_EdfReader_subsecond(self):
        f = pyedflib.EdfReader(self.edf_subsecond)
        self.assertEqual(f.getStartdatetime(), datetime(2020, 1, 24, 4, 5, 56, 39453))


    def test_EdfReader_ReadAnnotations(self):
        try:
            f = pyedflib.EdfReader(self.edf_data_file, pyedflib.DO_NOT_READ_ANNOTATIONS)
        except IOError:
            print('cannot open', self.edf_data_file)
            return

        ann_index, ann_duration, ann_text = f.readAnnotations()
        np.testing.assert_equal(ann_index.size, 0)

        del f

        try:
            f = pyedflib.EdfReader(self.edf_data_file, pyedflib.READ_ALL_ANNOTATIONS)
        except IOError:
            print('cannot open', self.edf_data_file)
            return

        ann_index, ann_duration, ann_text = f.readAnnotations()
        np.testing.assert_almost_equal(ann_index[0], 0)
        np.testing.assert_almost_equal(ann_index[1], 600)

        np.testing.assert_equal(f.signals_in_file, 11)
        np.testing.assert_equal(f.datarecords_in_file, 600)

        for i in np.arange(11):
            np.testing.assert_almost_equal(f.getSampleFrequencies()[i], 200)
            np.testing.assert_equal(f.getNSamples()[i], 120000)

        del f

    def test_EdfReader_Check_Size(self):
        sample_frequency = 100
        channel_info = {'label': 'test_label', 'dimension': 'mV', 'sample_rate': 256,
                        'sample_frequency': sample_frequency, 'physical_max': 1.0, 'physical_min': -1.0,
                        'digital_max': 8388607, 'digital_min': -8388608,
                        'prefilter': 'pre1', 'transducer': 'trans1'}
        f = pyedflib.EdfWriter(self.bdf_broken_file, 1, file_type=pyedflib.FILETYPE_BDFPLUS)
        f.setSignalHeader(0,channel_info)
        f.setTechnician('tec1')
        data = np.ones(100) * 0.1
        f.writePhysicalSamples(data)
        f.writePhysicalSamples(data)
        del f

        f = pyedflib.EdfReader(self.bdf_broken_file, pyedflib.READ_ALL_ANNOTATIONS, pyedflib.DO_NOT_CHECK_FILE_SIZE)
        np.testing.assert_equal(f.getTechnician(), 'tec1')

        np.testing.assert_equal(f.getLabel(0), 'test_label')
        np.testing.assert_equal(f.getPhysicalDimension(0), 'mV')
        np.testing.assert_equal(f.getPrefilter(0), 'pre1')
        np.testing.assert_equal(f.getTransducer(0), 'trans1')
        np.testing.assert_equal(f.getSampleFrequency(0), sample_frequency)

        # When both 'sample_rate' and 'sample_frequency' are present, we write
        # the file using the latter, which means that when we read it back,
        # only the 'sample_frequency' value is present.
        expected_signal_header = {**channel_info, 'sample_rate': sample_frequency}
        np.testing.assert_equal(f.getSignalHeader(0), expected_signal_header)
        np.testing.assert_equal(f.getSignalHeaders(), [expected_signal_header])
        del f

    def test_EdfReader_Close_file(self):
        f = pyedflib.EdfReader(self.edf_data_file)
        np.testing.assert_equal(f.getSignalLabels()[0], 'squarewave')

        # Don't close the file but try to reopen it and verify that it fails.
        with np.testing.assert_raises(IOError):
            ff = pyedflib.EdfReader(self.edf_data_file)
        
        # Now close and verify it can be re-opened/read.
        f.close()

        ff = pyedflib.EdfReader(self.edf_data_file)
        np.testing.assert_equal(ff.getSignalLabels()[0], 'squarewave')
        del f, ff

    def test_BdfReader_Read_accented_file(self):
        sample_frequency = 100
        channel_info = {'label': 'test_label', 'dimension': 'mV', 'sample_rate': 256,
                        'sample_frequency': sample_frequency, 'physical_max': 1.0, 'physical_min': -1.0,
                        'digital_max': 8388607, 'digital_min': -8388608,
                        'prefilter': 'pre1', 'transducer': 'trans1'}
        f = pyedflib.EdfWriter(self.bdf_accented_file, 1,file_type=pyedflib.FILETYPE_BDFPLUS)
        f.setSignalHeader(0,channel_info)
        f.setTechnician('tec1')
        data = np.ones(100) * 0.1
        f.writePhysicalSamples(data)
        f.writePhysicalSamples(data)
        del f

        f = pyedflib.EdfReader(self.bdf_accented_file, pyedflib.READ_ALL_ANNOTATIONS, pyedflib.DO_NOT_CHECK_FILE_SIZE)
        np.testing.assert_equal(f.getTechnician(), 'tec1')
        np.testing.assert_equal(f.getLabel(0), 'test_label')
        np.testing.assert_equal(f.getPhysicalDimension(0), 'mV')
        np.testing.assert_equal(f.getPrefilter(0), 'pre1')
        np.testing.assert_equal(f.getTransducer(0), 'trans1')

        # When both 'sample_rate' and 'sample_frequency' are present, we write
        # the file using the latter, which means that when we read it back,
        # only the 'sample_frequency' value is present.
        expected_signal_header = {**channel_info, 'sample_rate': sample_frequency}
        np.testing.assert_equal(f.getSignalHeader(0), expected_signal_header)
        np.testing.assert_equal(f.getSignalHeaders(), [expected_signal_header])
        del f


    def test_read_incorrect_file(self):

        # this should simply not be found and not trigger the UTF8 warning
        with self.assertRaises(FileNotFoundError):
            f = pyedflib.EdfReader('does_not_exist')

        # this file is corrupted and should be found, but not be read
        # so the Exception should be OSError and not FileNotFoundError
        with self.assertRaises(OSError):
            with open(self.tmp_edf_file, 'wb') as f:
                f.write(b'0123456789')
            f = pyedflib.EdfReader(self.tmp_edf_file)

        # now we create a file that is not EDF/BDF compliant
        # this should raise an OSError and not a FileNotFoundError
        with self.assertRaises(OSError) as cm:
            channel_info = {'label': 'test_label', 'dimension': 'mV', 'sample_rate': 256,
                            'sample_frequency': 100, 'physical_max': 1.0, 'physical_min': -1.0,
                            'digital_max': 8388607, 'digital_min': -8388608,
                            'prefilter': 'pre1', 'transducer': 'trans1'}
            with pyedflib.EdfWriter(self.bdf_accented_file, 1, file_type=pyedflib.FILETYPE_BDFPLUS) as f:
                f.setSignalHeader(0,channel_info)
                f.setTechnician('tec1')
                data = np.ones(100) * 0.1
                f.writePhysicalSamples(data)
    
            with open(self.bdf_accented_file, 'rb') as f:
                content = bytearray(f.read())
                content[181] = 58
            with open(self.bdf_accented_file, 'wb') as f:
                f.write(content)

            f = pyedflib.EdfReader(self.bdf_accented_file)
        # However, the error before should not be a FileNotFoundError
        assert not isinstance(cm.exception, FileNotFoundError)




if __name__ == '__main__':
    # run_module_suite(argv=sys.argv)
    unittest.main()
