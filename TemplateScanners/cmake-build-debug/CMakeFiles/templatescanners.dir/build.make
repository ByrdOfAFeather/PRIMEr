# CMAKE generated file: DO NOT EDIT!
# Generated by "Unix Makefiles" Generator, CMake Version 3.13

# Delete rule output on recipe failure.
.DELETE_ON_ERROR:


#=============================================================================
# Special targets provided by cmake.

# Disable implicit rules so canonical targets will work.
.SUFFIXES:


# Remove some rules from gmake that .SUFFIXES does not remove.
SUFFIXES =

.SUFFIXES: .hpux_make_needs_suffix_list


# Suppress display of executed commands.
$(VERBOSE).SILENT:


# A target that is always out of date.
cmake_force:

.PHONY : cmake_force

#=============================================================================
# Set environment variables for the build.

# The shell in which to execute make rules.
SHELL = /bin/sh

# The CMake executable.
CMAKE_COMMAND = /snap/clion/61/bin/cmake/linux/bin/cmake

# The command to remove a file.
RM = /snap/clion/61/bin/cmake/linux/bin/cmake -E remove -f

# Escaping for special characters.
EQUALS = =

# The top-level source directory on which CMake was run.
CMAKE_SOURCE_DIR = /home/byrdofafeather/ByrdOfAFeather/PRIMEr/TemplateScanners

# The top-level build directory on which CMake was run.
CMAKE_BINARY_DIR = /home/byrdofafeather/ByrdOfAFeather/PRIMEr/TemplateScanners/cmake-build-debug

# Include any dependencies generated for this target.
include CMakeFiles/templatescanners.dir/depend.make

# Include the progress variables for this target.
include CMakeFiles/templatescanners.dir/progress.make

# Include the compile flags for this target's objects.
include CMakeFiles/templatescanners.dir/flags.make

CMakeFiles/templatescanners.dir/TemplateScanners.cpp.o: CMakeFiles/templatescanners.dir/flags.make
CMakeFiles/templatescanners.dir/TemplateScanners.cpp.o: ../TemplateScanners.cpp
	@$(CMAKE_COMMAND) -E cmake_echo_color --switch=$(COLOR) --green --progress-dir=/home/byrdofafeather/ByrdOfAFeather/PRIMEr/TemplateScanners/cmake-build-debug/CMakeFiles --progress-num=$(CMAKE_PROGRESS_1) "Building CXX object CMakeFiles/templatescanners.dir/TemplateScanners.cpp.o"
	/usr/bin/c++  $(CXX_DEFINES) $(CXX_INCLUDES) $(CXX_FLAGS) -o CMakeFiles/templatescanners.dir/TemplateScanners.cpp.o -c /home/byrdofafeather/ByrdOfAFeather/PRIMEr/TemplateScanners/TemplateScanners.cpp

CMakeFiles/templatescanners.dir/TemplateScanners.cpp.i: cmake_force
	@$(CMAKE_COMMAND) -E cmake_echo_color --switch=$(COLOR) --green "Preprocessing CXX source to CMakeFiles/templatescanners.dir/TemplateScanners.cpp.i"
	/usr/bin/c++ $(CXX_DEFINES) $(CXX_INCLUDES) $(CXX_FLAGS) -E /home/byrdofafeather/ByrdOfAFeather/PRIMEr/TemplateScanners/TemplateScanners.cpp > CMakeFiles/templatescanners.dir/TemplateScanners.cpp.i

CMakeFiles/templatescanners.dir/TemplateScanners.cpp.s: cmake_force
	@$(CMAKE_COMMAND) -E cmake_echo_color --switch=$(COLOR) --green "Compiling CXX source to assembly CMakeFiles/templatescanners.dir/TemplateScanners.cpp.s"
	/usr/bin/c++ $(CXX_DEFINES) $(CXX_INCLUDES) $(CXX_FLAGS) -S /home/byrdofafeather/ByrdOfAFeather/PRIMEr/TemplateScanners/TemplateScanners.cpp -o CMakeFiles/templatescanners.dir/TemplateScanners.cpp.s

# Object files for target templatescanners
templatescanners_OBJECTS = \
"CMakeFiles/templatescanners.dir/TemplateScanners.cpp.o"

# External object files for target templatescanners
templatescanners_EXTERNAL_OBJECTS =

bin/templatescanners.so: CMakeFiles/templatescanners.dir/TemplateScanners.cpp.o
bin/templatescanners.so: CMakeFiles/templatescanners.dir/build.make
bin/templatescanners.so: /usr/local/lib/libopencv_dnn.so.4.0.1
bin/templatescanners.so: /usr/local/lib/libopencv_gapi.so.4.0.1
bin/templatescanners.so: /usr/local/lib/libopencv_ml.so.4.0.1
bin/templatescanners.so: /usr/local/lib/libopencv_objdetect.so.4.0.1
bin/templatescanners.so: /usr/local/lib/libopencv_photo.so.4.0.1
bin/templatescanners.so: /usr/local/lib/libopencv_stitching.so.4.0.1
bin/templatescanners.so: /usr/local/lib/libopencv_video.so.4.0.1
bin/templatescanners.so: /usr/lib/x86_64-linux-gnu/libboost_system.so
bin/templatescanners.so: /usr/lib/x86_64-linux-gnu/libboost_filesystem.so
bin/templatescanners.so: /usr/local/lib/libopencv_calib3d.so.4.0.1
bin/templatescanners.so: /usr/local/lib/libopencv_features2d.so.4.0.1
bin/templatescanners.so: /usr/local/lib/libopencv_flann.so.4.0.1
bin/templatescanners.so: /usr/local/lib/libopencv_highgui.so.4.0.1
bin/templatescanners.so: /usr/local/lib/libopencv_videoio.so.4.0.1
bin/templatescanners.so: /usr/local/lib/libopencv_imgcodecs.so.4.0.1
bin/templatescanners.so: /usr/local/lib/libopencv_imgproc.so.4.0.1
bin/templatescanners.so: /usr/local/lib/libopencv_core.so.4.0.1
bin/templatescanners.so: CMakeFiles/templatescanners.dir/link.txt
	@$(CMAKE_COMMAND) -E cmake_echo_color --switch=$(COLOR) --green --bold --progress-dir=/home/byrdofafeather/ByrdOfAFeather/PRIMEr/TemplateScanners/cmake-build-debug/CMakeFiles --progress-num=$(CMAKE_PROGRESS_2) "Linking C shared library bin/templatescanners.so"
	$(CMAKE_COMMAND) -E cmake_link_script CMakeFiles/templatescanners.dir/link.txt --verbose=$(VERBOSE)

# Rule to build all files generated by this target.
CMakeFiles/templatescanners.dir/build: bin/templatescanners.so

.PHONY : CMakeFiles/templatescanners.dir/build

CMakeFiles/templatescanners.dir/clean:
	$(CMAKE_COMMAND) -P CMakeFiles/templatescanners.dir/cmake_clean.cmake
.PHONY : CMakeFiles/templatescanners.dir/clean

CMakeFiles/templatescanners.dir/depend:
	cd /home/byrdofafeather/ByrdOfAFeather/PRIMEr/TemplateScanners/cmake-build-debug && $(CMAKE_COMMAND) -E cmake_depends "Unix Makefiles" /home/byrdofafeather/ByrdOfAFeather/PRIMEr/TemplateScanners /home/byrdofafeather/ByrdOfAFeather/PRIMEr/TemplateScanners /home/byrdofafeather/ByrdOfAFeather/PRIMEr/TemplateScanners/cmake-build-debug /home/byrdofafeather/ByrdOfAFeather/PRIMEr/TemplateScanners/cmake-build-debug /home/byrdofafeather/ByrdOfAFeather/PRIMEr/TemplateScanners/cmake-build-debug/CMakeFiles/templatescanners.dir/DependInfo.cmake --color=$(COLOR)
.PHONY : CMakeFiles/templatescanners.dir/depend

