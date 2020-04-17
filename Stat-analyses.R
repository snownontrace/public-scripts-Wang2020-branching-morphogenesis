### If not installed, install the 'rstudioapi' package
# install.packages('rstudioapi)
library('rstudioapi')

### Set the working directory to this source file to enable usage of relative path
setwd(dirname(rstudioapi::getActiveDocumentContext()$path))

tukey_hsd_test <- function(csv_file, colname_data, colname_groups) {
  ### This function implements straightforward ANOVA and Tukey HSD test
  ### for cleaned data in the tidy long form
  ### ============================================
  ### csv_file: path to the csv file storing the data for analysis,
  ###           it should have a header with the two columns below
  ### colname_data: the column name of the data for comparison
  ### colname_groups: the column name of the group anotation
  ### ============================================
  
  ## Open a text file sink to keep a record
  outputPrefix <- unlist( strsplit(basename(csv_file), '\\.') )[1]
  outputFilename <- file.path(dirname(csv_file), paste0(outputPrefix, '.txt'))
  sink(outputFilename)
  
  ## Read in the data frame
  df <- read.csv(csv_file)
  colnames(df)[grep(colname_data, colnames(df))] <- 'data_to_compare'
  colnames(df)[grep(colname_groups, colnames(df))] <- 'groups'
  
  ## Order the data by the groups annotation
  df <- df[order(df$groups),]
  df$groups <- factor(df$groups)
  
  ## perform one-way ANOVA and tukey test of all pairs of groups
  fm <- aov(data_to_compare ~ groups, data = df)
  print( 'Summary of ANOVA:', quote=FALSE )
  print( summary(fm) )
  
  tukey_test <- TukeyHSD(fm, 'groups')
  print( 'Summary of pairwise Tukey HSD test:', quote=FALSE )
  print(tukey_test[1]$groups)
  
  ## Close the sink file handle
  sink()
  
  ## plot the Tukey test mean comparisons
  # plot(TukeyHSD(fm, "groups"))
}

processFolder <- function(inputFolder) {
  ### perform tukey HSD test and keep a record for every csv file in inputFolder
  
  fileNames <- dir(inputFolder, pattern ='.csv') 
  for (fileName in fileNames) {
    fullFilePath <- file.path(inputFolder, fileName)
    tukey_hsd_test(fullFilePath, 'data_to_compare', 'groups')
  }
}

### Set how many digits to output for p values etc
options("scipen"=-1, "digits"=10)
processFolder('../data_cleaned/')

