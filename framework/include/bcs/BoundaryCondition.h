#ifndef BOUNDARYCONDITION_H
#define BOUNDARYCONDITION_H

#include "MooseObject.h"
#include "Coupleable.h"
#include "FunctionInterface.h"
#include "TransientInterface.h"
#include "MaterialPropertyInterface.h"
#include "PostprocessorInterface.h"
#include "GeometricSearchInterface.h"

// libMesh
#include "elem.h"
#include "vector_value.h"

class MooseVariable;
class MooseMesh;
class Problem;
class SubProblemInterface;

class BoundaryCondition :
  public MooseObject,
  public Coupleable,
  public FunctionInterface,
  public TransientInterface,
  public MaterialPropertyInterface,
  public PostprocessorInterface,
  protected GeometricSearchInterface
{
public:
  BoundaryCondition(const std::string & name, InputParameters parameters);
  virtual ~BoundaryCondition();

  unsigned int boundaryID() { return _boundary_id; }

  MooseVariable & variable() { return _var; }

  unsigned int coupledComponents(const std::string & varname);

  virtual void setup() { }

protected:
  Problem & _problem;
  SubProblemInterface & _subproblem;
  SystemBase & _sys;
  THREAD_ID _tid;
  MooseVariable & _var;
  MooseMesh & _mesh;
  int _dim;

  unsigned int _boundary_id;

  const Elem * & _current_elem;
  unsigned int & _current_side;

  const std::vector<Point> & _normals;

  // Single Instance Variables
  Real & _real_zero;
  Array<Real> & _zero;
  Array<RealGradient> & _grad_zero;
  Array<RealTensor> & _second_zero;
};


template<>
InputParameters validParams<BoundaryCondition>();

#endif /* BOUNDARYCONDITION_H_ */
