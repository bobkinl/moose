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

#include "NodalSum.h"
#include "MooseMesh.h"
#include "SubProblem.h"
// libMesh
#include "libmesh/boundary_info.h"

template<>
InputParameters validParams<NodalSum>()
{
  InputParameters params = validParams<NodalVariablePostprocessor>();
  return params;
}

NodalSum::NodalSum(const std::string & name, InputParameters parameters) :
    NodalVariablePostprocessor(name, parameters),
    _sum(0)
{
}

void
NodalSum::initialize()
{
  _sum = 0;
}

void
NodalSum::execute()
{
  _sum += _u[_qp];
}

Real
NodalSum::getValue()
{
  gatherSum(_sum);

  return _sum;
}

void
NodalSum::threadJoin(const UserObject & y)
{
  const NodalSum & pps = static_cast<const NodalSum &>(y);
  _sum += pps._sum;
}
