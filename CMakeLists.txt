##
 #######################################################################################################################
 #
 #  Copyright (c) 2024 Advanced Micro Devices, Inc. All Rights Reserved.
 #
 #  Permission is hereby granted, free of charge, to any person obtaining a copy
 #  of this software and associated documentation files (the "Software"), to deal
 #  in the Software without restriction, including without limitation the rights
 #  to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
 #  copies of the Software, and to permit persons to whom the Software is
 #  furnished to do so, subject to the following conditions:
 #
 #  The above copyright notice and this permission notice shall be included in all
 #  copies or substantial portions of the Software.
 #
 #  THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
 #  IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
 #  FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
 #  AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
 #  LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
 #  OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
 #  SOFTWARE.
 #
 #######################################################################################################################

cmake_minimum_required(VERSION 3.5)

PROJECT(spvgen VERSION 1 LANGUAGES C CXX)

option(SPVGEN_ENABLE_WERROR "Build with -Werror enabled" OFF)
option(SPVGEN_BUILD_STATIC "Build static library" OFF)
option(SPVGEN_BUILD_SHARED "Build shared library" ON)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

if (CMAKE_COMPILER_IS_GNUCC OR CMAKE_C_COMPILER_ID MATCHES "Clang")
	set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -fno-rtti -fPIC")
endif ()

set(CMAKE_MODULE_PATH ${CMAKE_MODULE_PATH} "${CMAKE_CURRENT_SOURCE_DIR}/cmake")

if(NOT DEFINED THIRD_PARTY_PATH)
    # Third_party path
    if(EXISTS ${PROJECT_SOURCE_DIR}/../third_party)
        set(THIRD_PARTY_PATH ${PROJECT_SOURCE_DIR}/../third_party CACHE PATH "The path of third_party.")
    endif()
endif()

add_definitions(-DNV_EXTENSIONS)

add_definitions(-DAMD_EXTENSIONS)

add_definitions(-DENABLE_HLSL)

# Disable unnecessary components in SPIRV-tools and SPIRV_CROSS
set(SPIRV_SKIP_TESTS TRUE CACHE BOOL "" FORCE)
set(SPIRV_SKIP_EXECUTABLES ON CACHE BOOL "OGLP override." FORCE)
set(SPIRV_CROSS_ENABLE_TESTS OFF CACHE BOOL "OGLP override." FORCE)
set(SPIRV_CROSS_CLI OFF CACHE BOOL "OGLP override." FORCE)

# Build third party targets
if(EXISTS ${THIRD_PARTY_PATH}/SPIRV-tools)
    set(SPIRV_TOOLS_PATH ${THIRD_PARTY_PATH}/SPIRV-tools)
else()
    set(SPIRV_TOOLS_PATH ${PROJECT_SOURCE_DIR}/external/SPIRV-tools)
endif()
set(SPIRV_WERROR ${SPVGEN_ENABLE_WERROR} CACHE BOOL "${PROJECT_NAME} override." FORCE)
add_subdirectory(${SPIRV_TOOLS_PATH} external/SPIRV-tools)

if(EXISTS ${THIRD_PARTY_PATH}/glslang)
    set(GLSLANG_PATH ${THIRD_PARTY_PATH}/glslang)
else()
    set(GLSLANG_PATH ${PROJECT_SOURCE_DIR}/external/glslang)
endif()
add_subdirectory(${GLSLANG_PATH} external/glslang)

if(EXISTS ${THIRD_PARTY_PATH}/SPIRV-cross)
    set(SPIRV_CROSS_PATH ${THIRD_PARTY_PATH}/SPIRV-cross)
else()
    set(SPIRV_CROSS_PATH ${PROJECT_SOURCE_DIR}/external/SPIRV-cross)
endif()
add_subdirectory(${SPIRV_CROSS_PATH} external/SPIRV-cross)

set(SPVGEN_SOURCE_FILES
    source/spvgen.cpp
)

# Build object library
add_library(spvgen_base OBJECT ${SPVGEN_SOURCE_FILES})

target_include_directories(spvgen_base
PUBLIC
    include
PRIVATE
    ${GLSLANG_PATH}
    ${GLSLANG_PATH}/SPIRV
    ${SPIRV_TOOLS_PATH}/include
    ${SPIRV_CROSS_PATH}
)

target_link_libraries(spvgen_base glslang SPIRV SPIRV-Tools SPIRV-Tools-opt spirv-cross-c)

# Touch an empty source file
set(EMPTY_SOURCE_FILES ${CMAKE_CURRENT_BINARY_DIR}/empty.cpp)
add_custom_command(
    OUTPUT  ${EMPTY_SOURCE_FILES}
    COMMAND ${CMAKE_COMMAND} -E touch ${EMPTY_SOURCE_FILES}
    COMMENT "Touching ${EMPTY_SOURCE_FILES}"
)

# Build static library
if (SPVGEN_BUILD_STATIC)
    add_library(spvgen_static STATIC ${EMPTY_SOURCE_FILES})
    target_link_libraries(spvgen_static spvgen_base)
endif()

# Build shared library
if (SPVGEN_BUILD_SHARED)
    add_library(spvgen SHARED ${EMPTY_SOURCE_FILES})
    target_link_libraries(spvgen spvgen_base)
    set_target_properties(spvgen PROPERTIES PREFIX "")
endif()
