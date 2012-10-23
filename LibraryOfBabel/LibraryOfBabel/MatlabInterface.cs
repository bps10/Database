using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;
using EngMATLib;

namespace LibraryOfBabel
{
    class MatlabInterface
    {
        public void Matrix()
        {
            using (EngMATAccess mat = new EngMATAccess())
            {
                mat.Evaluate("A = [1 2 3; 4 5 6]");
                double [,] mx = null;
                mat.GetMatrix("A", ref mx);
            }
        }
    }
}
