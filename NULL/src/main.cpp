/**************************************
 **** 2017-4-23      ******************
 **** Abdulhakim Qahtan ****************
 **** aqahtan@hbku.edu.qa ****************
 ***************************************/


#include "csv_reader.h"
#include "Profiler.h"
#include "common.h"
#include "DV_Detector.h"
#include "OD.h"
#include "RandDMVD.h"
#include "Patterns.h"
#include <dirent.h>
#include <cstdlib>

 long max_num_terms_per_att = 200;


bool DirectoryExists( const char* pzPath )
{
    if ( pzPath == NULL) return false;

    DIR *pDir;
    bool bExists = false;

    pDir = opendir (pzPath);

    if (pDir != NULL)
    {
        bExists = true;    
        (void) closedir (pDir);
    }

    return bExists;
}
// ========================================================================
string splitpath(const std::string str, 
                  const char delimiter){
    int i, j, k;
    // cout << str << endl;
    for(i = str.length(); i >= 0; i --){
        if (delimiter == str[i])
            break;
    }
    // cout << "i = " << i << "   string length = " << str.length() << endl;
    if ((i == 0) && (str[i] != delimiter)) i = -1;  
    std::string result = str.substr (i+1,str.length()-1);
    return result;
}


// ========================================================================
void Print_output_data(string output_dir, string tab_name, std::vector<sus_disguised> sus_dis_values){
    if (output_dir[output_dir.length()-1] != '/')
        output_dir += '/';
    char delim = '/';
    string out_f_name = splitpath(tab_name, delim);
    string table_name = out_f_name.substr (0,out_f_name.length()-4);
    // cerr << table_name << endl;
    out_f_name = "DMV_"+out_f_name;
    string out_file_name = output_dir + out_f_name;
    fstream ofs(out_file_name, ios::out);
    if (!ofs.good()){
        cerr << "Problem opening output file .... \n" << out_file_name << endl;;
        return;
    }
    if (sus_dis_values.size() < 1)
        return;
    ofs << "Table Name" << "," << "Attribute Name" << "," 
             << "DMV" 
             << "," << "Frequency"
             << "," << "Detecting Tool" 
             << endl;

    for (long i = 0; i < (long)sus_dis_values.size(); i++)
        ofs << check_d_quotation(table_name) << "," << check_d_quotation(sus_dis_values[i].attr_name) << "," 
             << check_d_quotation(sus_dis_values[i].value) 
             << "," << sus_dis_values[i].frequency
             << "," << sus_dis_values[i].tool_name 
             << endl;
    
    ofs.close();
}

// Function to generate CSV-formatted string
char* GenerateCSV(const std::string& tab_name, const std::vector<sus_disguised>& sus_dis_values) {
    std::stringstream csv_stream;

    // CSV header
    csv_stream << "column_name,value,frequency,category\n";

    // CSV rows
    for (size_t i = 0; i < sus_dis_values.size(); i++) {
        csv_stream << check_d_quotation(sus_dis_values[i].attr_name) << "," 
                   << check_d_quotation(sus_dis_values[i].value) 
                   << "," << sus_dis_values[i].frequency
                   << "," << "NULL Value"
                   << "\n";
    }

    std::string str = csv_stream.str();
    char* cstr = new char[str.size() + 1]; // 加1以包含末尾的空字符
    std::strcpy(cstr, str.c_str());
    return cstr;
}



// ================The main Function====================================
extern "C"
// ================The main Function====================================
const char* start(char * table_name, int tool_id){ 

    string file_name = string(table_name);
    int t_id = tool_id;

    
    std::vector<sus_disguised> sus_dis_values;
    while(!sus_dis_values.empty())
        sus_dis_values.pop_back();

    doubleVecStr P;
    CSV_READER *dataReader = new CSV_READER();  
    Table T = dataReader->read_csv_file(file_name);
    cerr << T.table_name << "  has :" << T.data.size() << "  tuples" 
         << "  and  " << T.data[0].size() << "  attributes." << endl;

    RandDMVD RandD;
    DataProfiler * dvdDataProfiler = new DataProfiler();
    TableProfile TP;
    vector<struct item> most_common;
    DV_Detector DVD;
    OD od;
    vector<map<string, long> > tablehist =  dvdDataProfiler->TableHistogram(T);
    TP = dvdDataProfiler->profile_table(T, tablehist);
    pattern_learner * PL = new pattern_learner();
    switch(t_id){
        case 1:
            //PL->find_all_patterns(tablehist, TP, sus_dis_values);
            //Print_output_data(full_output_path, T.table_name, sus_dis_values);
            DVD.check_non_conforming_patterns(TP, tablehist, sus_dis_values);
            break;
        case 2:
            sus_dis_values = RandD.find_disguised_values(T, tablehist, max_num_terms_per_att);
            break;
        case 3:
            od.detect_outliers(TP, sus_dis_values);
            break;
        case 4: 
            sus_dis_values = RandD.find_disguised_values(T, tablehist, max_num_terms_per_att);
            //PL->find_all_patterns(tablehist, TP, sus_dis_values);
            //Print_output_data(full_output_path, T.table_name, sus_dis_values);
            DVD.check_non_conforming_patterns(TP, tablehist, sus_dis_values);
            //od.detect_outliers(TP, sus_dis_values);
            break;
        default:
            cerr << "Unkown option .. " << t_id << endl;
    }
    char*  csv = GenerateCSV(T.table_name, sus_dis_values);
    return  csv;
}