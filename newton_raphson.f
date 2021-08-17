      program newton_raphson_test
        implicit none
        real*8 root
        root = newton_raphson(0.5d0)
        print *, root
      
      contains
      
      function f(x)
        implicit none
        real*8, intent(in) :: x
        real*8 f
        f = x**4.0d0 - 2.0d0*x**2.0d0 + 0.25d0
      end function f

      function fprime(x)
        implicit none
        real*8, intent(in) :: x
        real*8 fprime
        fprime = 4.0d0*x**3.0d0 - 4.0d0*x
      end function fprime
      
      function newton_raphson(x0)
        ! Purpose: Newton-Raphson iteration to find the root of a
        ! scalar function.
        ! Variable dictionary:
        ! x0 = initial guess
        ! maxiter = maximum number of iterations
        ! k = iteration counter
        ! tol = convergence tolerance+
        ! f = Eq. 88 (external function)
        ! fprime = Eq. 89 (external function)
        ! fx = value of f at current x
        ! fxprime = value of fprime at current x
        ! d = increment
        implicit none
        real*8 newton_raphson, x, x0, d
        real*8 func, func_derivative, fx, fxprime, tol
        integer k, maxiter
        parameter (maxiter=100, tol=1.0d-6)
        ! intial guess
        x = x0
        ! Newton iteration to find a zero of func 
        do k = 1, maxiter
          ! evaluate function and its derivative:
          fxprime = fprime(x)
          if (fxprime == 0.0d0) then
            print *, "Function derivative is 0 at initial x"
            stop
          end if
          fx = f(x)
          if (abs(fx) < tol) then
            newton_raphson = x
            return
          end if
          ! compute Newton-Raphson increment d:
          d = fx/fxprime
          ! update x:
          x = x - d
        end do
        pause "Exceeded maximum number of iterations"
      end function newton_raphson
      end program newton_raphson_test