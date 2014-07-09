/****************************************************************/
/*               DO NOT MODIFY THIS HEADER                      */
/* MOOSE - Multiphysics Object Oriented Simulation Environment  */
/*                                                              */
/*           (c) 2010 Battelle Energy Alliance, LLC             */
/*                   ALL RIGHTS RESERVED                        */
/*                                                              */
/*          Prepared by Battelle Energy Alliance, LLC           */
/*            Under Contract No. DE-AC07-05ID14517              */
/*            With the U. S. Department of Energy               */
/*                                                              */
/*            See COPYRIGHT for full restrictions               */
/****************************************************************/

#ifndef MOOSEERROR_H
#define MOOSEERROR_H

#include "Moose.h"

// libMesh includes
#include "libmesh/print_trace.h"

/**
 * MOOSE wrapped versions of useful libMesh macros (see libmesh_common.h)
 */
#define mooseError(msg)                                                             \
  do                                                                                \
  {                                                                                 \
    Moose::err << "\n\n"                                                            \
               << (Moose::__color_console ? RED : "")                               \
               << "\n\n*** ERROR ***\n"                                             \
               << msg                                                               \
               << (Moose::__color_console ? DEFAULT : "")                           \
               << "\n\n";                                                           \
    if (libMesh::global_n_processors() == 1)                                        \
      print_trace();                                                                \
    libmesh_here();                                                                 \
    MPI_Abort(libMesh::GLOBAL_COMM_WORLD,1);                                        \
    exit(1);                                                                        \
  } while (0)

#ifdef NDEBUG
#define mooseAssert(asserted, msg)
#else
#define mooseAssert(asserted, msg)                                                  \
  do                                                                                \
  {                                                                                 \
    if (!(asserted))                                                                \
    {                                                                               \
      Moose::err                                                                    \
        << (Moose::__color_console ? RED : "")                                      \
        << "\n\nAssertion `" #asserted "' failed\n"                                 \
        << msg                                                                      \
        << "\nat "                                                                  \
        << __FILE__ << ", line " << __LINE__                                        \
        << (Moose::__color_console ? DEFAULT : "")                                  \
        << std::endl;                                                               \
     if (libMesh::global_n_processors() == 1)                                       \
       print_trace();                                                               \
     libmesh_here();                                                                \
     MPI_Abort(libMesh::GLOBAL_COMM_WORLD,1);                                       \
     exit(1);                                                                       \
    }                                                                               \
  } while (0)
#endif

#define mooseWarning(msg)                                                           \
  do                                                                                \
  {                                                                                 \
    Moose::out                                                                      \
      << (Moose::__color_console ? YELLOW : "")                                     \
      << "\n\n*** Warning ***\n"                                                    \
      << msg                                                                        \
      << "\nat " << __FILE__ << ", line " << __LINE__                               \
      << (Moose::__color_console ? DEFAULT : "")                                    \
      << "\n"                                                                       \
      << std::endl;                                                                 \
  } while (0)

#define mooseDoOnce(do_this) do { static bool did_this_already = false; if (!did_this_already) { did_this_already = true; do_this; } } while (0)

#define mooseDeprecated()                                                                              \
    mooseDoOnce(                                                                                       \
      Moose::out                                                                                       \
      << (Moose::__color_console ? YELLOW : "")                                                        \
      << "*** Warning, This code is deprecated, and likely to be removed in future library versions! " \
      << __FILE__ << ", line " << __LINE__ << ", compiled "                                            \
      << __DATE__ << " at " << __TIME__ << " ***"                                                      \
      << (Moose::__color_console ? DEFAULT : "")                                                       \
      << std::endl;                                                                                    \
      )

#define mooseCheckMPIErr(err) do { if (err != MPI_SUCCESS) { if (libMesh::global_n_processors() == 1) print_trace(); libmesh_here(); MPI_Abort(libMesh::GLOBAL_COMM_WORLD,1); exit(1); } } while (0)

#endif /* MOOSEERRORS_H */
