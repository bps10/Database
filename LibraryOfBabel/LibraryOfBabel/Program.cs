using System;
using System.Collections.Generic;
using System.Linq;
using System.Threading.Tasks;
using System.Windows.Forms;
using System.IO;
using System.Reflection;
using IronPython.Hosting;
using Microsoft.Scripting.Hosting;
using Microsoft.Scripting.Utils;

namespace LibraryOfBabel
{
    static class Program
    {
        /// <summary>
        /// The main entry point for the application.
        /// </summary>
        [STAThread]

        static void Main(string[] args)
        {
            ScriptEngine pyEngine = Python.CreateEngine();

            Assembly h5class = Assembly.LoadFile(Path.GetFullPath("BabelPython.dll"));
            pyEngine.Runtime.LoadAssembly(h5class);
            ScriptScope pyScope = pyEngine.Runtime.ImportModule("BabelPython");

            // Get the Python Class
            object Database = pyEngine.Operations.Invoke(pyScope.GetVariable("Database"));

            // Invoke a method of the class
            pyEngine.Operations.InvokeMember(Database, "ImportAllData", new object[0]);

            // create a callable function to 'ImportAllData'
            Action CallData = pyEngine.Operations.GetMember<Action>(Database, "ImportAllData");
            //CallData();


            Application.EnableVisualStyles();
            Application.SetCompatibleTextRenderingDefault(false);
            Application.Run(new Form1());
        }
       
    }
}
