from lnbits.db import Connection


async def m001_initial(db: Connection):
    await db.execute(
        f"""
       CREATE TABLE pay2print.printer (
           id TEXT PRIMARY KEY,
           user_id TEXT NOT NULL,
           wallet TEXT NOT NULL,
           name TEXT NOT NULL,
           host TEXT NOT NULL,
           amount INTEGER NOT NULL,
           width INTEGER NOT NULL,
           height INTEGER NOT NULL,
           created_at TIMESTAMP NOT NULL DEFAULT {db.timestamp_now}
       );
   """
    )
    await db.execute(
        f"""
       CREATE TABLE pay2print.print (
           payment_hash TEXT PRIMARY KEY,
           printer TEXT NOT NULL,
           payment_status TEXT NOT NULL,
           print_status TEXT NOT NULL,
           file TEXT NOT NULL,
           updated_at TIMESTAMP NOT NULL DEFAULT {db.timestamp_now},
           created_at TIMESTAMP NOT NULL DEFAULT {db.timestamp_now}
       );
   """
    )
