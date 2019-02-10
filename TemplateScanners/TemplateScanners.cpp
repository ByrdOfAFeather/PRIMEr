//
// Created by byrdofafeather on 2/7/19.
//

#include <utility>
#include <bits/stdc++.h>
#include <map>
#include <cassert>
#include <opencv2/core/core.hpp>
#include <opencv2/highgui/highgui.hpp>
#include <iostream>
#include <opencv2/imgproc/imgproc.hpp>
#include <boost/python.hpp>
#include <Python.h>

using namespace std;
using namespace cv;
using namespace boost::python;

typedef std::map<std::string, std::deque<std::string>> DescriptorToTemplatesMap;

class Timestamp {
public:
    double time;
    std::string descriptor;
    Timestamp() = default;

    Timestamp (std::string initDescriptor, double initTime) {
        time = initTime;
        descriptor = std::move(initDescriptor);
    }
};

class TemplateScanner {
public:
    std::map<std::string, std::deque<cv::Mat>> templateMats;
    double templateThreshold;

    // TODO: Remake this vector int a deque
    TemplateScanner(const DescriptorToTemplatesMap &templatePaths, double threshold){
        templateMats = build_image_threshold_hash(templatePaths);
        templateThreshold = threshold;
    };

    std::map<std::string, std::deque<cv::Mat>> build_image_threshold_hash(const DescriptorToTemplatesMap &templatePaths) {
        std::map<std::string, std::deque<cv::Mat>> returnMap;
        for (auto const& currentItems: templatePaths) {
            std::string currentDescriptor = currentItems.first;
            std::deque<std::string> paths = currentItems.second;
            for (const std::string &currentPath: paths) {
                cv::Mat loadedImage = imread(currentPath, cv::IMREAD_COLOR);
                if (loadedImage.empty()) { cout << "FAILED TO LOAD IMAGE "; cout << currentPath << endl;}
                cv::Mat reversedImage;
                cv::flip(loadedImage, reversedImage, 1);
                std::deque<cv::Mat> images = returnMap[currentDescriptor];
                images.push_front(loadedImage);
                images.push_front(reversedImage);
                returnMap[currentDescriptor] = images;
            }
        }
        return returnMap;
    }

    double match_template(cv::Mat image, cv::Mat templateToMatch, int filterProcess) {
        cv::Mat result;
        int resultCols = image.cols - templateToMatch.cols + 1;
        int resultRows = image.rows - templateToMatch.rows + 1;
        result.create(resultRows, resultCols, CV_32FC1);

        cv::matchTemplate(image, templateToMatch, result, filterProcess);

        double minVal; double maxVal; cv::Point minLoc; cv::Point maxLoc; cv::Point matchLoc;

        cv::minMaxLoc(result, &minVal, &maxVal, &minLoc, &maxLoc, cv::Mat());

        return maxVal;
    }

    std::string get_best_match(const cv::Mat &image) {
        std::map<std::string, double> positive;
        for (auto const& currentValues : templateMats) {
            std::string currentDescriptor = currentValues.first;
            std::deque<cv::Mat> currentImages = currentValues.second;

            double currentDescriptorMaxProbability = 0;
            for (cv::Mat &currentImage: currentImages) {
                double currentMaxProbability = match_template(image, currentImage, cv::TM_CCOEFF_NORMED);
                if (currentMaxProbability >= templateThreshold) {
                    if (currentDescriptorMaxProbability < currentMaxProbability) {
                        currentDescriptorMaxProbability = currentMaxProbability;
                    }
                }
            }
            positive[currentDescriptor] = currentDescriptorMaxProbability;
        }

        if (positive.size() > 1) {
            int mostProbableDescriptorValue = 0;
            std::string mostProbableDescriptor;
            for (auto const &currentMaxes : positive) {
                std::string currentDescriptor = currentMaxes.first;
                double currentDescriptorMaxValue = currentMaxes.second;
                if (mostProbableDescriptorValue < currentDescriptorMaxValue) {
                    mostProbableDescriptor = currentDescriptor;
                }
            }
            return mostProbableDescriptor;
        }

        else if (positive.size() == 1) {
            for (auto const &finalValue : positive) { return finalValue.first; }
        }

        else { return ""; }
    }

    std::string scan(const cv::Mat &image) {
        std::string currentMaxDescriptor = get_best_match(image);
        return currentMaxDescriptor;
    }


};

class VideoScannerThreaded: public TemplateScanner {
public:
    int frameIndexes[2]{};
    std::string videoPath;

    VideoScannerThreaded(const DescriptorToTemplatesMap &templatePaths, std::string initVideoPath,
            int frameIndexStart, int frameIndexEnd, double threshold);

    std::deque<Timestamp> get_timestamps() {
        cv::VideoCapture video(videoPath);
        assert(video.get(cv::CAP_PROP_FRAME_COUNT) != 0);

        std::deque<Timestamp> timestamps;

        video.set(cv::CAP_PROP_POS_FRAMES, frameIndexes[0]);
        double fps = video.get(cv::CAP_PROP_FPS);

        while(true) {

            cv::Mat currentFrame;
            video.read(currentFrame);

            if (video.get(cv::CAP_PROP_POS_FRAMES) < frameIndexes[1] && !currentFrame.empty()) {
                std::string exportDescriptor = scan(currentFrame);
                if (!exportDescriptor.empty()) {
                    cout << "EXPORTING : ";
                    cout << video.get(cv::CAP_PROP_POS_MSEC) / 1000 << endl;
                    cout << "EXPORTING : ";
                    cout << exportDescriptor << endl;

                    Timestamp currentTime(exportDescriptor, video.get(cv::CAP_PROP_POS_MSEC) / 1000);
                    timestamps.push_front(currentTime);
                }
                double currentFrameNumber = video.get(cv::CAP_PROP_POS_FRAMES);
                video.set(cv::CAP_PROP_POS_FRAMES, currentFrameNumber + fps);
            }

            else {
                break;
            }
        }
        return timestamps;
    }
};

VideoScannerThreaded::VideoScannerThreaded(const DescriptorToTemplatesMap &templatePaths,
                                           std::string initVideoPath, int frameIndexStart, int frameIndexEnd,
                                           double threshold) : TemplateScanner(templatePaths, threshold) {
    frameIndexes[0] = frameIndexStart;
    frameIndexes[1] = frameIndexEnd;
    videoPath = std::move(initVideoPath);
}

class VideoThreader {
public:
    DescriptorToTemplatesMap templates;
    double threshold;

    VideoThreader(DescriptorToTemplatesMap initTemplatePaths, double initThreshold) {
        templates = initTemplatePaths;
        threshold = initThreshold;
    }

    std::deque<Timestamp> thread_scanners(const std::string &videoPath, int divisor = 1800) {
        cv::VideoCapture video(videoPath);
        double frame_count = video.get(cv::CAP_PROP_FRAME_COUNT);
        assert(frame_count != 0);

        std::deque<std::future<std::deque<Timestamp>>> futures;
        int frameSections = 0;
        int currentFrameStart = 0;
        int currentFrameEnd = 0;
        while (frame_count > divisor * frameSections) {
            VideoScannerThreaded currentVideoScanner(templates, videoPath, currentFrameStart, currentFrameEnd,
                                                     threshold);
            std::promise<std::deque<Timestamp>> currentReturnPromise;
            std::future<std::deque<Timestamp>> currentPromisedFuture = std::async(&VideoScannerThreaded::get_timestamps,
                    currentVideoScanner);
            futures.push_front(std::move(currentPromisedFuture));
            currentFrameStart += divisor;
            currentFrameEnd += divisor * 2;
            frameSections += 1;
        }

        cout << "===== STARTING " + std::to_string(frameSections) + " THREADS =====" << endl;

        std::deque<Timestamp> allTimestamps;
        for (std::future<std::deque<Timestamp>> &future : futures) {
            std::deque<Timestamp> currentTimestamps = future.get();
            for (Timestamp &timestamp : currentTimestamps) {
                allTimestamps.push_front(timestamp);
            }
        }
        return allTimestamps;
    }
};

struct ThreadedVideoScan {
public:
    ThreadedVideoScan() = default;
    //    void static run(std::map<std::string, std::vector<std::string>> templates, std::string videoPath,
//            double threshold) {

    boost::python::list run(boost::python::dict templates, boost::python::str pythonVideoPath, double threshold) {
//        std::map<std::string, std::vector<std::string>> templates;
//        double threshold = 0;
//        std::vector<std::string> path;
//        path.emplace_back("Sources/0.png");
//        templates["jump"] = path;
        DescriptorToTemplatesMap final;
        std::string videoPath = boost::python::extract<std::string>(pythonVideoPath);
        boost::python::list keys = templates.keys();
        for (int i = 0; i < boost::python::len(keys); i++) {
            std::string currentKey = boost::python::extract<std::string>(keys[i]);
            std::deque<std::string> currentPaths;
            boost::python::list paths = boost::python::extract<boost::python::list>(templates[currentKey]);
            for (int j = 0; j < boost::python::len(paths); j++) {
                currentPaths.push_front(boost::python::extract<std::string>(paths[j]));
            }

            final[currentKey] = currentPaths;
        }
        VideoThreader scanner(final, threshold);

//        std::string videoPath = "Sources/mm.mp4";
        std::deque<Timestamp> cTimestamps = scanner.thread_scanners(videoPath);
        boost::python::list pythonTimestamps;
        for (Timestamp &time : cTimestamps) {
                pythonTimestamps.append(boost::python::object(Timestamp(time.descriptor, time.time)));
        }
        return pythonTimestamps;
    }
};


int main() {
    return 0;
}

BOOST_PYTHON_MODULE(TemplateScanners) {
//    class_<std::map<std::string, std::deque<std::string>>>("DescriptorToTemplatesMap")
//            .def(boost::python::map_indexing_suite<std::map<std::wstring, std::deque<std::wstring>>());

    class_<ThreadedVideoScan>("ThreadedVideoScan")
            .def("run", &ThreadedVideoScan::run);

    class_<Timestamp>("Timestamp")
            .def_readonly("time", &Timestamp::time)
            .def_readonly("marker", &Timestamp::descriptor);
}
