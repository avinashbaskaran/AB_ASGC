--------------------------------------------------------------------------------------------
FILE ORGANIZATION
--------------------------------------------------------------------------------------------
DBs_raw: 			Two unprocessed datasets (described below), and an 
	 			image descrbing the hand grasps recorded in the dataset

data: 	 			Data from datasets referenced by the code in this 
				repository
--------------------------------------------------------------------------------------------






--------------------------------------------------------------------------------------------
DATA DESCRIPTION:
--------------------------------------------------------------------------------------------
(This repository makes use of secondary data published in open source repositories
please see the DATA SOURCE section below for full description of the source of this data)

FILE: 				data\male_1.mat 
DESCRIPTION: 			Contains parent data set of 2-channel sEMG readings 
				for various hand grasps

FILE: 				data\cylindricalGraspChannel1.csv
DESCRIPTION: 			A subset of data from the parent set; this file 
	     			contains joint sEMG readings from the region of 
	     			muscles that include the Flexor Capri Ulnaris 
				and Extensor Capri Radialis muscles

FILE: 				data\cylindricalGraspChannel1.csv
DESCRIPTION: 			A subset of data from the parent set; this file 
	     			contains joint sEMG readings from the region of 
	     			muscles that include the Flexor Capri Ulnaris 
				and Extensor Capri Radialis muscles


FILE: 				data\cylindricalGraspChannel1.csv
DESCRIPTION: 			A subset of data from the parent set; this file 
	     			contains joint sEMG readings from the region of 
				muscles that include the Longus and Brevis muscles
--------------------------------------------------------------------------------------------






--------------------------------------------------------------------------------------------
DATA SOURCE:
--------------------------------------------------------------------------------------------
Test data was adapted from a Center for Machine Learning and Intelligent Systems
open source repository. Data and the following text was adapted from this web address:
https://archive.ics.uci.edu/ml/datasets/sEMG+for+Basic+Hand+movements#)
 


(source) Abstract: 		The sEMG for Basic Hand movements includes 
	  			2 databases of surface electromyographic 
	  			signals of 6 hand movements using Delsys'
	  			EMG System. Healthy subjects conducted six 
				daily life grasps.



Data Set Characteristics:  	Time-Series
Number of Instances:		3000
Attribute Characteristics:	Real
Number of Attributes:		2500
Date Donated:			2014-11-18
Associated Tasks:		Classification
Number of Web Hits:		78547
Source:				Christos Sapsanis (csapsanis @ gmail.com) and Anthony Tzes
				ANeMoS Lab
				School of Electrical and Computer Engineering
				University of Patras;
				G. Georgoulas
				KIC Laboratory	
				Department of Informatics and Telecommunications Technology,
				Technological Educational Institute of Epirus



Data Set Information:
Instrumentation:		The data were collected at a sampling 
				rate of 500 Hz, using as a programming 
				kernel the National Instruments (NI) 
				Labview. The signals were band-pass 
				filtered using a Butterworth Band Pass 
				filter with low and high cutoff at 15Hz 
				and 500Hz respectively and a notch filter 
				at 50Hz to eliminate line interference 
				artifacts.

				The hardware that was used was an NI 
				analog/digital conversion card NI USB- 009, 
				mounted on a PC. The signal was taken from 
				two Differential EMG Sensors and the signals 
				were transmitted to a 2-channel EMG system 
				by Delsys Bagnoliâ Handheld EMG Systems.



Original Protocol:		The experiments consisted of freely and 
				repeatedly grasping of different items, 
				which were essential to conduct the hand 
				movements. The speed and force were 
				intentionally left to the subjects will. 
				There were two forearm surface EMG electrodes 
				Flexor Capri Ulnaris and Extensor Capri 
				Radialis, Longus and Brevis) held in place 
				by elastic bands and the reference electrode 
				in the middle, in order to gather information 
				about the muscle activation.

				The subjects were asked to perform repeatedly 
				the following six movements, which can be 
				considered as daily hand grasps:

				a) Spherical: for holding spherical tools
				b) Tip: for holding small tools
				c) Palmar: for grasping with palm facing the object
				d) Lateral: for holding thin, flat objects
				e) Cylindrical: for holding cylindrical tools
				f) Hook: for supporting a heavy load



Databases included:		1) 5 healthy subjects (two males and three females) 
				of the same age approximately (20 to 22-year-old) 
				conducted the six grasps for 30 times each. The 
				measured time is 6 sec. There is a mat file available 
				for every subject.

				2) 1 healthy subject (male, 22-year-old) conducted the 
				six grasps for 100 times each for 3 consecutive days. 
				The measured time is 5 sec. There is a mat file 
				available for every day.



Attribute Information:
Data Format:			The format of each mat file is the following: (The data 
				per grasp and per channel are in separate table with an 
				obvious naming.)

				Spherical --> (spher_ch1, spher_ch2), 
				Tip --> (tip_ch1, tip_ch2), 
				Palmar --> (palm_ch1, palm_ch2), 
				Lateral --> (lat_ch1, lat_ch2), 
				Cylindrical --> (cyl_ch1, cyl_ch2), 
				Hook --> (hook_ch1, hook_ch2)}

				Each row of these tables has the whole signal per trial. 
				The signal value is measured in Voltage.

				In summary, in each subject, there will be a mat file with 
				12 matrixes, in which matrix there will be 30 (trials) rows 
				and 3000 (points of the signal) columns for database 1 (or 
				100 rows and 2500 columns for database 2).



Relevant Papers:		Since the data is signals in time domain, part of it can be 
				used for classification using signal processing techniques 
				and methods, such as Empirical Mode Decomposition (EMD). 
				Moreover, suggested features for extraction can be 
				Integrated Electromyogram (IEMG), Zero Crossing (ZC), 
				Slope Sign Changes (SSC), Waveform Length (WL), 
				Willison Amplitude (WAMP) etc.

				More information can be found in the following paper:
				C. Sapsanis, G. Georgoulas, A. Tzes, EMG based classification 
				of basic hand movements based on time-frequency features in 
				21th IEEE Mediterranean Conference on Control and Automation 
				(MED 13), June 25 - 28, pp. 716 - 722, 2013.



Citation Request:		If you found useful these databases, please cite the following:
				For the database 1: C. Sapsanis, G. Georgoulas, A. Tzes, 
				D. Lymberopoulos, Improving EMG based classification of 
				basic hand movements using EMD in 35th Annual International 
				Conference of the IEEE Engineering in Medicine and Biology 
				Society 13 (EMBC 13), July 3-7, pp. 5754 - 5757, 2013.
				
				For the database 2: C. Sapsanis, Recognition of Basic Hand 
				Movements Using Electromyography, Diploma Thesis, University 
				of Patras, 2013
				
				BibTex
				@mastersthesis{sapsanis2013recognition,
				title={Recognition of basic hand movements using Electromyography},
				author={Sapsanis, Christos},
				school={University of Patras} ,
				year={2013}
				}
--------------------------------------------------------------------------------------------
--------------------------------------------------------------------------------------------
--------------------------------------------------------------------------------------------
--------------------------------------------------------------------------------------------
--------------------------------------------------------------------------------------------
