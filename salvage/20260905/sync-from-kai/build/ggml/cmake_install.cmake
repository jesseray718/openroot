# Install script for directory: /data/data/com.termux/files/home/llama.cpp-fix/ggml

# Set the install prefix
if(NOT DEFINED CMAKE_INSTALL_PREFIX)
  set(CMAKE_INSTALL_PREFIX "/usr/local")
endif()
string(REGEX REPLACE "/$" "" CMAKE_INSTALL_PREFIX "${CMAKE_INSTALL_PREFIX}")

# Set the install configuration name.
if(NOT DEFINED CMAKE_INSTALL_CONFIG_NAME)
  if(BUILD_TYPE)
    string(REGEX REPLACE "^[^A-Za-z0-9_]+" ""
           CMAKE_INSTALL_CONFIG_NAME "${BUILD_TYPE}")
  else()
    set(CMAKE_INSTALL_CONFIG_NAME "Release")
  endif()
  message(STATUS "Install configuration: \"${CMAKE_INSTALL_CONFIG_NAME}\"")
endif()

# Set the component getting installed.
if(NOT CMAKE_INSTALL_COMPONENT)
  if(COMPONENT)
    message(STATUS "Install component: \"${COMPONENT}\"")
    set(CMAKE_INSTALL_COMPONENT "${COMPONENT}")
  else()
    set(CMAKE_INSTALL_COMPONENT)
  endif()
endif()

# Install shared libraries without execute permission?
if(NOT DEFINED CMAKE_INSTALL_SO_NO_EXE)
  set(CMAKE_INSTALL_SO_NO_EXE "0")
endif()

# Is this installation the result of a crosscompile?
if(NOT DEFINED CMAKE_CROSSCOMPILING)
  set(CMAKE_CROSSCOMPILING "FALSE")
endif()

# Set path to fallback-tool for dependency-resolution.
if(NOT DEFINED CMAKE_OBJDUMP)
  set(CMAKE_OBJDUMP "/data/data/com.termux/files/usr/bin/llvm-objdump")
endif()

if(NOT CMAKE_INSTALL_LOCAL_ONLY)
  # Include the install script for the subdirectory.
  include("/data/data/com.termux/files/home/llama.cpp-fix/build/ggml/src/cmake_install.cmake")
endif()

if(CMAKE_INSTALL_COMPONENT STREQUAL "Unspecified" OR NOT CMAKE_INSTALL_COMPONENT)
  foreach(file
      "$ENV{DESTDIR}${CMAKE_INSTALL_PREFIX}/lib/libggml.so.0.15.3"
      "$ENV{DESTDIR}${CMAKE_INSTALL_PREFIX}/lib/libggml.so.0"
      )
    if(EXISTS "${file}" AND
       NOT IS_SYMLINK "${file}")
      file(RPATH_CHECK
           FILE "${file}"
           RPATH "")
    endif()
  endforeach()
  file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/lib" TYPE SHARED_LIBRARY FILES
    "/data/data/com.termux/files/home/llama.cpp-fix/build/bin/libggml.so.0.15.3"
    "/data/data/com.termux/files/home/llama.cpp-fix/build/bin/libggml.so.0"
    )
  foreach(file
      "$ENV{DESTDIR}${CMAKE_INSTALL_PREFIX}/lib/libggml.so.0.15.3"
      "$ENV{DESTDIR}${CMAKE_INSTALL_PREFIX}/lib/libggml.so.0"
      )
    if(EXISTS "${file}" AND
       NOT IS_SYMLINK "${file}")
      file(RPATH_CHANGE
           FILE "${file}"
           OLD_RPATH "/data/data/com.termux/files/home/llama.cpp-fix/build/bin:"
           NEW_RPATH "")
      if(CMAKE_INSTALL_DO_STRIP)
        execute_process(COMMAND "/data/data/com.termux/files/usr/bin/llvm-strip" "${file}")
      endif()
    endif()
  endforeach()
endif()

if(CMAKE_INSTALL_COMPONENT STREQUAL "Unspecified" OR NOT CMAKE_INSTALL_COMPONENT)
  file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/lib" TYPE SHARED_LIBRARY FILES "/data/data/com.termux/files/home/llama.cpp-fix/build/bin/libggml.so")
endif()

if(CMAKE_INSTALL_COMPONENT STREQUAL "Unspecified" OR NOT CMAKE_INSTALL_COMPONENT)
  file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/include" TYPE FILE FILES
    "/data/data/com.termux/files/home/llama.cpp-fix/ggml/include/ggml.h"
    "/data/data/com.termux/files/home/llama.cpp-fix/ggml/include/ggml-cpu.h"
    "/data/data/com.termux/files/home/llama.cpp-fix/ggml/include/ggml-alloc.h"
    "/data/data/com.termux/files/home/llama.cpp-fix/ggml/include/ggml-backend.h"
    "/data/data/com.termux/files/home/llama.cpp-fix/ggml/include/ggml-blas.h"
    "/data/data/com.termux/files/home/llama.cpp-fix/ggml/include/ggml-cann.h"
    "/data/data/com.termux/files/home/llama.cpp-fix/ggml/include/ggml-cpp.h"
    "/data/data/com.termux/files/home/llama.cpp-fix/ggml/include/ggml-cuda.h"
    "/data/data/com.termux/files/home/llama.cpp-fix/ggml/include/ggml-opt.h"
    "/data/data/com.termux/files/home/llama.cpp-fix/ggml/include/ggml-metal.h"
    "/data/data/com.termux/files/home/llama.cpp-fix/ggml/include/ggml-rpc.h"
    "/data/data/com.termux/files/home/llama.cpp-fix/ggml/include/ggml-virtgpu.h"
    "/data/data/com.termux/files/home/llama.cpp-fix/ggml/include/ggml-sycl.h"
    "/data/data/com.termux/files/home/llama.cpp-fix/ggml/include/ggml-vulkan.h"
    "/data/data/com.termux/files/home/llama.cpp-fix/ggml/include/ggml-webgpu.h"
    "/data/data/com.termux/files/home/llama.cpp-fix/ggml/include/ggml-zendnn.h"
    "/data/data/com.termux/files/home/llama.cpp-fix/ggml/include/ggml-openvino.h"
    "/data/data/com.termux/files/home/llama.cpp-fix/ggml/include/gguf.h"
    )
endif()

if(CMAKE_INSTALL_COMPONENT STREQUAL "Unspecified" OR NOT CMAKE_INSTALL_COMPONENT)
  foreach(file
      "$ENV{DESTDIR}${CMAKE_INSTALL_PREFIX}/lib/libggml-base.so.0.15.3"
      "$ENV{DESTDIR}${CMAKE_INSTALL_PREFIX}/lib/libggml-base.so.0"
      )
    if(EXISTS "${file}" AND
       NOT IS_SYMLINK "${file}")
      file(RPATH_CHECK
           FILE "${file}"
           RPATH "")
    endif()
  endforeach()
  file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/lib" TYPE SHARED_LIBRARY FILES
    "/data/data/com.termux/files/home/llama.cpp-fix/build/bin/libggml-base.so.0.15.3"
    "/data/data/com.termux/files/home/llama.cpp-fix/build/bin/libggml-base.so.0"
    )
  foreach(file
      "$ENV{DESTDIR}${CMAKE_INSTALL_PREFIX}/lib/libggml-base.so.0.15.3"
      "$ENV{DESTDIR}${CMAKE_INSTALL_PREFIX}/lib/libggml-base.so.0"
      )
    if(EXISTS "${file}" AND
       NOT IS_SYMLINK "${file}")
      if(CMAKE_INSTALL_DO_STRIP)
        execute_process(COMMAND "/data/data/com.termux/files/usr/bin/llvm-strip" "${file}")
      endif()
    endif()
  endforeach()
endif()

if(CMAKE_INSTALL_COMPONENT STREQUAL "Unspecified" OR NOT CMAKE_INSTALL_COMPONENT)
  file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/lib" TYPE SHARED_LIBRARY FILES "/data/data/com.termux/files/home/llama.cpp-fix/build/bin/libggml-base.so")
endif()

if(CMAKE_INSTALL_COMPONENT STREQUAL "Unspecified" OR NOT CMAKE_INSTALL_COMPONENT)
  file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/lib/cmake/ggml" TYPE FILE FILES
    "/data/data/com.termux/files/home/llama.cpp-fix/build/ggml/ggml-config.cmake"
    "/data/data/com.termux/files/home/llama.cpp-fix/build/ggml/ggml-version.cmake"
    )
endif()

string(REPLACE ";" "\n" CMAKE_INSTALL_MANIFEST_CONTENT
       "${CMAKE_INSTALL_MANIFEST_FILES}")
if(CMAKE_INSTALL_LOCAL_ONLY)
  file(WRITE "/data/data/com.termux/files/home/llama.cpp-fix/build/ggml/install_local_manifest.txt"
     "${CMAKE_INSTALL_MANIFEST_CONTENT}")
endif()
