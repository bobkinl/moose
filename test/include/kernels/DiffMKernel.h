#ifndef DIFFMKERNEL_H
#define DIFFMKERNEL_H

#include "Kernel.h"
#include "MaterialProperty.h"

// Forward Declaration
class DiffMKernel;

template<>
InputParameters validParams<DiffMKernel>();


class DiffMKernel : public Kernel
{
public:
  DiffMKernel(const std::string & name, InputParameters parameters);

protected:
  virtual Real computeQpResidual();

  virtual Real computeQpJacobian();

  std::string _prop_name;
  MaterialProperty<Real> & _diff;
  Real _offset;
};
#endif //DIFFMKERNEL_H
