import pandas as pd
from standings_extract import extract_step


def flatten_details(df):
	standings = df.drop(columns="details", errors="ignore").copy()
	detail_rows = df[["id", "details"]].explode("details", ignore_index=True)
	detail_rows = detail_rows[detail_rows["details"].notna()]

	if detail_rows.empty:
		return standings

	details = pd.json_normalize(detail_rows["details"])
	details["id"] = detail_rows["id"].to_numpy()
	details = details.rename(columns={"type.code": "detail_type"})

	detail_columns = (
		details.pivot_table(
			index="id",
			columns="detail_type",
			values="value",
			aggfunc="first",
		)
		.reset_index()
	)
	detail_columns.columns.name = None

	return standings.merge(detail_columns, on="id", how="left")


main_df = flatten_details(extract_step["standings_bundesliga26_27"])
print(main_df)