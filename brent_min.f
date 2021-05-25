        program brent_min_test
          implicit none
          real*8 xresult, val
          val = brent_min(0.0d0,1.0d0,1.0d-8,xresult,f)
          print *, val, xresult
        contains
        
        function f(x)
          implicit none
          real*8, intent(in) :: x
          real*8 f
          f = x**4.0d0 - 2.0d0*x**2.0d0 + 0.25d0
        end function f
        
        function brent_min(ax,bx,tol,xmin,func)
          ! Purpose: This routine determines the minimum value of a
          ! scalar function func, between ax and bx. The abscissa of the
          ! minimum is returned as xmin, and the minimum function value
          ! is returned as brent, the returned function value.
          ! Adapted from Numerical Recipes in Fortran 77 and the fmin
          ! routine from the Netlib repository.
          implicit none
          ! input variables
          real*8, intent(in) :: ax,bx,tol
          ! local variables
          integer itmax,iter
          real*8 cgold,xmin,func
          real*8 a,b,d,e,etemp,fu,fv,fw,fx,p,q,r,tol1,tol2,u,v,w,x,xm
          parameter (itmax=100,cgold=.3819660d0)
          ! output variables
          real*8 brent

          a = ax
          b = bx
          v = a + cgold*(b - a)
          w = v
          x = v
          e =0.0d0 ! This will be the distance moved on the step before last.
          fx = func(x)
          fv = fx
          fw = fx
          do iter = 1,itmax ! Main program loop.
            xm = 0.5d0*(a + b)
            tol1 = tol*abs(x) + tol/3.0d0
            tol2 = 2.0d0*tol1
            if (abs(x - xm) <= (tol2 - 0.5d0*(b - a))) then ! Test for done here.
              xmin = x
              brent = fx
              return
            end if
            p = 0.0d0 ! initialize variables for parabolic fit
            q = 0.0d0
            if (abs(e) > tol1) then 
              r = (x - w)*(fx - fv) ! Construct a trial parabolic
              q = (x - v)*(fx - fw)
              p = (x - v)*q - (x - w)*r
              q =  2.0d0*(q - r)
              if (q > 0.0d0) p = -p
              q = abs(q)
              etemp = e
              e = d
            end if
            if (abs(p) >= abs(0.5d0*q*etemp).or.p <= q*(a - x).or.
     1          p >= q*(b - x)) then ! Check acceptability of the parabolic fit
              if(x >= xm) then ! Take golden section step
                e = a - x
              else
                e = b - x
              end if
              d = cgold * e
            else
              d = p / q ! Take the parabolic step.
              u = x + d
              if (u - a < tol2 .or. b - u < tol2) then
                d = sign(tol1,xm - x)
              end if
            end if
            if(abs(d) >= tol1) then ! Arrive here with d computed either from parabolic fit or from golden section.
              u = x + d 
            else
              u = x + sign(tol1,d)
            end if
            fu = func(u) ! This is the one function evaluation per iteration,
            if (fu <= fx) then ! and now we have to decide what to do with our function
              if (u >= x) then ! evaluation. Housekeeping follows:
                a = x
              else
                b = x
              end if
              v = w
              fv = fw
              w = x
              fw = fx
              x = u
              fx = fu
            else
              if (u < x) then
                a = u
              else
                b = u
              end if
              if (fu <= fw .or. w == x) then
                v = w
                fv = fw
                w = u
                fw = fu
              else if(fu <= fv .or. v == x .or. v == w) then
                v = u
                fv = fu
              end if
            end if ! Done with housekeeping. Back for another iteration.
          end do
          pause 'Exceeded maximum iterations'
        end function brent_min
        end program brent_min_test