package agolang

func Remove(slc []string, del_str string) []string {
	result := []string{}
	start_i := 0
	for k, v := range slc {
		if v == del_str {
			result = append(result, slc[start_i:k]...)
			start_i = k + 1
		}
	}
	result = append(result, slc[start_i:len(slc)]...)
	return result
}
