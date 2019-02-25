##### TESTING #####
# import datetime
# from TemplateScanners import ThreadedVideoScan
# from VideoProcessing.Template import Template

# start = datetime.datetime.now()
# print(datetime.datetime.now())
# VideoScannerThreader = ThreadedVideoScan()
# VideoScannerThreader.run({"Jump": ["Sources/0.png"]}, "Sources/mm.mp4", .7)
# end = datetime.datetime.now()
# print(f"THIS IS THE DIFFERENCE {end - start}")

# start = datetime.datetime.now()
# print(datetime.datetime.now())
# from VideoProcessing import Template
#
# slow = ThreadedVideoScan({"Jump": [Template.Template(1, "Sources/0.png", "Jump")]}, "Sources/mm.mp4")
# slow.start()
# end = datetime.datetime.now()
# print(f"THIS IS THE DIFFERENCE {end - start}")
