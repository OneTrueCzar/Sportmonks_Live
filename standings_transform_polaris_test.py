import polars as pl
from standings_extract_polaris import extract_step_polars

polars_epl = extract_step_polars['standings_epl26_27'].clone()


def flatten_sportmonks(df):
	details_wide = (
		df
		.select(pl.col('id').alias('parent_id'), 'details')
		.explode('details')
		.drop_nulls('details')
		.unnest('details')
		.select(
			pl.col('parent_id').alias('id'),
			pl.col('type').struct.field('code').alias('detail_type'),
			'value',
		)
		.pivot(
			on='detail_type',
			index='id',
			values='value',
			aggregate_function='first',
		)
	)

	final_df = (
		df
		.drop('details')
		.join(details_wide, on='id', how='left')
	)

	return final_df

def transform_step(extract_step):
	return {
		name: flatten_sportmonks(df)
		for name, df in extract_step.items()
	}

print(transform_step(extract_step_polars))